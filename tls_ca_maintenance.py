"""Check/remove the two affected trust anchors from bundled Python CA files.

Run after installing dependencies. certifi>=2026.10.19 and pip>=26.2.2
are the primary updates; this handles older gRPC/botocore bundled stores.
Reference: https://seclists.org/oss-sec/2026/q4/233
Only exact DER SHA-256 identities are removed, never certificate names.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import ssl
import sysconfig

REVOKED_ROOTS = {
    '86a1ecba089c4a8d3bbe2734c612ba341d813e043cf9e8a862cd5c57a36bbe6b': 'emSign ECC Root CA - G3',
    'd7a7a0fb5d7e2731d771e9484ebcdef71d5f0c3e0a2948782bc83ee0ea699ef4': 'AAA Certificate Services (cross-sign path)',
}
BUNDLES = ('certifi/cacert.pem', 'pip/_vendor/certifi/cacert.pem',
           'grpc/_cython/_credentials/roots.pem', 'botocore/cacert.pem')
CERT = re.compile(rb'-----BEGIN CERTIFICATE-----.*?-----END CERTIFICATE-----', re.S)

def sanitize(data):
    removed=[]
    def replace(match):
        der=ssl.PEM_cert_to_DER_cert(match[0].decode('ascii'))
        digest=hashlib.sha256(der).hexdigest()
        if digest in REVOKED_ROOTS:
            removed.append(REVOKED_ROOTS[digest]);return b''
        return match[0]
    result=CERT.sub(replace,data)
    if not CERT.search(result):raise ValueError('Refusing an empty CA bundle')
    return result,removed

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply',action='store_true')
    parser.add_argument('--backup-dir',type=Path)
    args=parser.parse_args()
    if args.apply and not args.backup_dir:parser.error('--apply requires --backup-dir')
    site=Path(sysconfig.get_path('purelib'));results=[]
    for relative in BUNDLES:
        path=site/relative
        if not path.exists():continue
        before=path.read_bytes();after,removed=sanitize(before)
        if removed and args.apply:
            dst=args.backup_dir/relative;dst.parent.mkdir(parents=True,exist_ok=True)
            if dst.exists():raise FileExistsError('Backup already exists: '+str(dst))
            dst.write_bytes(before)
            # Validate the result before touching the installed bundle.
            ctx=ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            ctx.load_verify_locations(cadata=b'\n'.join(CERT.findall(after)).decode('ascii'))
            path.write_bytes(after)
        results.append({'path':str(path),'removed' if args.apply else 'remaining':removed})
    print(json.dumps(results,ensure_ascii=False,indent=2))
    return 0 if args.apply or not any(x['remaining'] for x in results) else 1

if __name__=='__main__':raise SystemExit(main())
