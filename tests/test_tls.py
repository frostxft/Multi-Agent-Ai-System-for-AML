"""Verify Uvicorn's real TLS transport with an explicitly trusted test certificate."""
import ipaddress
import socket
import ssl
import threading
import time
from datetime import datetime,timedelta,timezone
from dataclasses import replace
import httpx
import uvicorn
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes,serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from aml.api import create_app

def test_https_with_verified_certificate(pipeline,tmp_path):
    key=rsa.generate_private_key(public_exponent=65537,key_size=2048)
    name=x509.Name([x509.NameAttribute(NameOID.COMMON_NAME,'localhost')])
    now=datetime.now(timezone.utc)
    cert=(x509.CertificateBuilder().subject_name(name).issuer_name(name).public_key(key.public_key())
          .serial_number(x509.random_serial_number()).not_valid_before(now-timedelta(minutes=1))
          .not_valid_after(now+timedelta(days=1))
          .add_extension(x509.SubjectAlternativeName([x509.DNSName('localhost'),x509.IPAddress(ipaddress.ip_address('127.0.0.1'))]),critical=False)
          .add_extension(x509.BasicConstraints(ca=True,path_length=None),critical=True).sign(key,hashes.SHA256()))
    cert_path=tmp_path/'test-cert.pem';key_path=tmp_path/'test-key.pem'
    cert_path.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    key_path.write_bytes(key.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption()))
    sock=socket.socket();sock.bind(('127.0.0.1',0))
    port=sock.getsockname()[1]
    settings=replace(pipeline.settings,reviewer_token='test-tls-reviewer')
    server=uvicorn.Server(uvicorn.Config(create_app(settings,pipeline),ssl_keyfile=str(key_path),ssl_certfile=str(cert_path),log_level='error'))
    thread=threading.Thread(target=server.run,kwargs={'sockets':[sock]},daemon=True);thread.start()
    try:
        deadline=time.monotonic()+10
        while not server.started and thread.is_alive() and time.monotonic()<deadline:time.sleep(.02)
        assert server.started
        context=ssl.create_default_context(cafile=str(cert_path))
        with httpx.Client(verify=context,trust_env=False) as client:
            response=client.get(f'https://127.0.0.1:{port}/api/health',headers={'Authorization':'Bearer test-tls-reviewer'})
        assert response.status_code==200
        assert response.json()['mode']=='token_rbac'
        assert response.headers['x-content-type-options']=='nosniff'
    finally:
        server.should_exit=True;thread.join(timeout=10);sock.close()
