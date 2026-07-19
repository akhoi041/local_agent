# Talos Code Signing

Talos 0.6.0 Beta may be distributed unsigned while the publisher certificate is being prepared, but that state must be explicit in the release folder. Public commercial releases should be signed before distribution.

## Policy

- Signing policy lives in `config/signing_policy.json`.
- Release artifacts are the standalone executable and Windows installer listed in `release_manifest.json`.
- Hashes are always recorded with SHA-256.
- A signed release must use Authenticode with SHA-256 file digest, SHA-256 timestamp digest, and a trusted timestamp server.
- An unsigned Pre-Alpha/Beta must be marked by `signing_status.json` and release notes must mention that Windows SmartScreen may warn on first launch.

## Prerequisites For Signing

- Windows SDK `signtool.exe`.
- An OV or EV code-signing certificate for `T-Engine`.
- Certificate available in the current user's certificate store, referenced by thumbprint or subject.
- Network access to the timestamp server configured in `config/signing_policy.json`.

## Commands

Record the current Pre-Alpha/Beta as deliberately unsigned:

```powershell
.\scripts\sign_release.ps1 -ReleaseDir releases\<versioned-release-folder> -AllowUnsignedBeta
```

Sign by certificate thumbprint:

```powershell
.\scripts\sign_release.ps1 -ReleaseDir releases\<versioned-release-folder> -CertificateThumbprint "<thumbprint>"
```

Sign by certificate subject:

```powershell
.\scripts\sign_release.ps1 -ReleaseDir releases\<versioned-release-folder> -CertificateSubject "T-Engine"
```

The script signs every `.exe` artifact in the release folder, verifies each artifact with `Get-AuthenticodeSignature`, and writes `signing_status.json`.

## Manual Verification

```powershell
Get-AuthenticodeSignature releases\<versioned-release-folder>\Talos-<version>-<channel>.exe
Get-AuthenticodeSignature releases\<versioned-release-folder>\Talos-<version>-<channel>-setup.exe
Get-FileHash releases\<versioned-release-folder>\Talos-<version>-<channel>.exe -Algorithm SHA256
Get-FileHash releases\<versioned-release-folder>\Talos-<version>-<channel>-setup.exe -Algorithm SHA256
```

## Release Rule

The release gate can ship only if the release folder contains either:

- Valid Authenticode signatures for the executable and installer, or
- A deliberate unsigned Pre-Alpha/Beta status file created with `-AllowUnsignedBeta`.

For 0.6.0, the current release posture is explicit unsigned Beta unless a T-Engine code-signing certificate is configured before the release gate.
