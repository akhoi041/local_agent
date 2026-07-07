# Talos Code Signing

Talos 0.2.0 Beta may be distributed unsigned while the publisher certificate is being prepared, but that state must be explicit in the release folder. Public commercial releases should be signed before distribution.

## Policy

- Signing policy lives in `config/signing_policy.json`.
- Release artifacts are the standalone executable and Windows installer listed in `release_manifest.json`.
- Hashes are always recorded with SHA-256.
- A signed release must use Authenticode with SHA-256 file digest, SHA-256 timestamp digest, and a trusted timestamp server.
- An unsigned Beta must be marked by `signing_status.json` and release notes must mention that Windows SmartScreen may warn on first launch.

## Prerequisites For Signing

- Windows SDK `signtool.exe`.
- An OV or EV code-signing certificate for `T-Engine`.
- Certificate available in the current user's certificate store, referenced by thumbprint or subject.
- Network access to the timestamp server configured in `config/signing_policy.json`.

## Commands

Record the current Beta as deliberately unsigned:

```powershell
.\scripts\sign_release.ps1 -ReleaseDir releases\Talos-0.2.0-beta -AllowUnsignedBeta
```

Sign by certificate thumbprint:

```powershell
.\scripts\sign_release.ps1 -ReleaseDir releases\Talos-0.2.0-beta -CertificateThumbprint "<thumbprint>"
```

Sign by certificate subject:

```powershell
.\scripts\sign_release.ps1 -ReleaseDir releases\Talos-0.2.0-beta -CertificateSubject "T-Engine"
```

The script signs every `.exe` artifact in the release folder, verifies each artifact with `Get-AuthenticodeSignature`, and writes `signing_status.json`.

## Manual Verification

```powershell
Get-AuthenticodeSignature releases\Talos-0.2.0-beta\Talos-0.2.0-beta.exe
Get-AuthenticodeSignature releases\Talos-0.2.0-beta\Talos-0.2.0-beta-setup.exe
Get-FileHash releases\Talos-0.2.0-beta\Talos-0.2.0-beta.exe -Algorithm SHA256
Get-FileHash releases\Talos-0.2.0-beta\Talos-0.2.0-beta-setup.exe -Algorithm SHA256
```

## Release Rule

The release gate can ship only if the release folder contains either:

- Valid Authenticode signatures for the executable and installer, or
- A deliberate unsigned-Beta status file created with `-AllowUnsignedBeta`.
