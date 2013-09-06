# Galah-Installer Protocol Version 1

The Galah-Installer application needs to be able to do a number of network related things securely:

 * Determine whether the current version of some program (Galah or dependencies) is up to date.
 * Determine where to find a particular version of some program.
 * Download a particular version of some program.

## Security Considerations

PGP is used throughout Galah-Installer. The latest version of GnuPG should be used to do the encryption. Galah-Installer is capable of keeping GnuPG up to date, but a working version of the program must be available on the system to begin with (chicken and egg problem).

Because Galah-Installer uses vanilla HTTP for its communication with the outside world, it may be vulnerable to a man-in-the-middle attack where the attacker DoS's the program by sending a super massive file from a request. Therefore maximum file sizes should be strictly enforced.

## Discovery

The first time Galah-Installer starts up, it should send a `GET` request for `http://gi.galahgroup.com/version-listing.json` and `http://gi.galahgroup.com/version-listing.json.pgp`. AFTER verifying that the file is properly signed with the stored key (by default, the *Galah Group Release Key*), it should parse the JSON data which will be laid out as follows.

```json
{
	"GnuPG": ["1.0.0", "2.0.1"],
	"galah-installer": ["0.1.0", "0.1.1"],
	"galah-core/web": ["0.2.0", "0.2.1", "0.2.2"],
	"galah-core/sisyphus": ["0.2.0", "0.2.1", "0.2.2"],
	"galah-core/shepherd": ["0.2.0", "0.2.1", "0.2.2"],
	"galah-core/sheep": ["0.2.0", "0.2.1", "0.2.2"],
	"galah-core/models": ["0.2.0", "0.2.1", "0.2.2"],
	"galah-discontinued-program": ["0.2.0", "DISCONTINUED"],
	"mongodb": ["1.0", "1.1"],
	"nginx": ["1.2", "1.3"]
}
```

The version number will be listed in order, and Galah-Installer should assume that the last item in each list is the latest version. Currently, versions are released following the rules laid out by [Semantic Versioning 2.0.0](http://semver.org/spec/v2.0.0.html) but this may change in the future. Galah-Installer should not do any sorting itself, though it may do a sanity check and refuse to update if the ordering is not what it thinks it should be.

If `DISCONTINUED` is listed as the most recent version, the program is no longer supported and should be uninstalled. A program may be resumed after it has been discontinued, in which case the `DISCONTINUED` string will be removed from the list and versions will proceed normally.

Galah-Installer should cache the version listing files and the HTTP headers received (notably the `LastModified` and `ContentLength` headers). Then, rather than sending `GET` requests every time it needs to check to see if new versions are available, it can send a `HEAD` request and compare the `LastModified` and `ContentLength` pair to see if both match exactly with the cached values.

## Getting Specific Version Info

After the Galah-Installer has decided that it needs to upgrade (or downgrade) it should send a `GET` request to `http://gi.galahgroup.com/version-info/PROGRAM-NAME/VERSION.json` (ex: `http://gi.galahgroup.com/galah-core/sheep/1.0.3.json`) and its corresponding PGP key (`http://gi.galahgroup.com/version-info/PROGRAM-NAME/VERSION.json.pgp`). It should also grab the versions between the version being moved to and the old version so no migrations are missed. AFTER verifying the JSON file is properly signed, Galah-Installer should parse the JSON and see something like the following.

```json
{
	"name": "galah-core/models",
	"version": "1.0.3",
	"compatible-with": {
		"galah-core/shepherd": ["1.0.2", "1.0.3"],
		"galah-core/sheep": ["1.0.2", "1.0.3"],
		"galah-core/web": ["1.0.2", "1.0.3"],
		"galah-core/models": ["1.0.3"],
		"redis": ["1.0.0"]
	},
	"require-offline": ["galah-core/shepherd", "galah-core/web"],
	"migrations": ["mongodb"],
	"installer-mirrors": ["http://gi.galahgroup.com/files/installer/galah-core/models/1.0.3.py"],
	"archive-mirrors": ["http://gi.galahgroup.com/files/archive/galah-core/models/1.0.3.tar.gz"],
	"migration-mirrors": ["http://gi.galahgroup.com/files/migration/galah-core/models/1.0.3.py"]
}
```

**compatible-with** lists versions of various programs that the new version will work with. If some program that is listed exists in your cluster but that program's version is not listed, that program must be upgraded first.

**require-offline** lists programs that cannot be running in your cluster during the upgrade process. These programs should be shut down or sent into offline mode (if supported) before performing the upgrade.

**migrations** lists any database programs that need to have migrations performed on them. When upgrading/downgrading from one version to another, all migrations between the two version must be performed. To keep things simple, only the program `galah-core/models` will have migrations.

The various **mirrors** lists specify where to find necessary files. Each location should be hit from left to right (so the first item in the list should be hit first, and if that URL is down the next is tried). Each file has a corresponding PGP signature that can be found by adding the extension `.pgp` to the end of the file name. Signatures should always be verified before the data received is interpreted at all.
