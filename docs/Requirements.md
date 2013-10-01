# Galah-Installer Protocol Version 1

The Galah-Installer application needs to be able to do a number of network related tasks securely:

 * Determine whether the current version of some program (Galah or dependencies) is up to date.
 * Determine where to find a particular version of some program.
 * Download a particular version of some program.

## Security Considerations

The Galah-Installer can run remotely pulled installation scripts with strong privileges on potentially powerful servers. Therefore security is of utmost concern and importance in its design.

### Signatures

All files pulled over the Internet have signatures associated with them. These signatures are generated in accordance with RSASSA-PSS as defined in [RFC3447](http://www.ietf.org/rfc/rfc3447.txt) (page 29), and the implementation provided by PyCrypto is used. For some great analysis of the RSASSA-PSS algorithm, see [this paper](http://rsapss.hboeck.de/rsapss.pdf).

All files should be verified against its signature and the trusted public key distributed with the installer. The hash algorithm used is `SHA-512` (SHA-2 with an output size of 512 bits). The RSA key length when signing is currently 16384 bits.

### DOS

Because Galah-Installer uses HTTP for its communication with the outside world, it may be vulnerable to a man-in-the-middle attack where the attacker DoS's the program by sending an HTTP response that is super massive and fills up the file system. This attack vector is unlikely as it requires strong access to the network, however, it can be mitigated through the use of a paranoid HTTP library. This will not be taken care of until after the initial release due to its high cost.

### Compromised Private Key

Though vulnerabilities due to Galah-Installer's use of cryptographic functions are certainly possible that would allow successful attacks, it is doubtful that such an attack would occur. A more likely attack is compromise of the key used to make releases combined with an attack to trick the installer into pulling down a malicious file. Such an attack would be very dangerous and could potentially infect all installations.

## Discovery

The first time Galah-Installer starts up, it should send a `GET` request for `http://gi.galahgroup.com/version-listing.json` and `http://gi.galahgroup.com/version-listing.json.sig`. AFTER verifying that the file is properly signed with the correct key, it should parse the JSON data which will be laid out as follows.

```json
{
	"packages": {
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
}
```

The backwards compatible listing value should always be checked. If the installer's current version is listed, it should immediately try to upgrade itself to the listed version

The version numbers will be listed in order, and Galah-Installer should assume that the last item in each list is the latest version. Currently, versions are released following the rules laid out by [Semantic Versioning 2.0.0](http://semver.org/spec/v2.0.0.html) but this may change in the future. Galah-Installer should not do any sorting itself, though it may do a sanity check and refuse to update if the ordering is not what it thinks it should be.

If `DISCONTINUED` is listed as the most recent version, the program is no longer supported and should be uninstalled. A program may be resumed after it has been discontinued, in which case the `DISCONTINUED` string will be removed from the list and versions will proceed normally.

Galah-Installer should cache the version listing files and the HTTP headers received (notably the `LastModified` and `ContentLength` headers). Then, rather than sending `GET` requests every time it needs to check to see if new versions are available, it can send a `HEAD` request and compare the `LastModified` and `ContentLength` pair to see if both match exactly with the cached values.

## Getting Specific Version Info

After the Galah-Installer has decided that it needs to upgrade (or downgrade) it should send a `GET` request to `http://gi.galahgroup.com/version-info/PROGRAM-NAME/VERSION.json` (ex: `http://gi.galahgroup.com/galah-core/sheep/1.0.3.json`) and its corresponding signature (`http://gi.galahgroup.com/version-info/PROGRAM-NAME/VERSION.json.sig`). It should also grab the versions between the version being moved to and the old version so no migrations are missed. AFTER verifying the JSON file(s) is properly signed, Galah-Installer should parse the JSON and see something like the following.

```json
{
	"name": "galah-core/models",
	"version": "1.0.3",

	"embedded": false,

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

**migrations** lists any database programs that need to have migrations performed on them. When upgrading/downgrading from one version to another, all migrations between the two version must be performed.

The various **mirrors** lists specify where to find necessary files. Each location should be hit from left to right (so the first item in the list should be hit first, and if that URL is down the next is tried). Each file has a corresponding signature that can be found by adding the extension `.sig` to the end of the file name. Signatures should always be verified before the data received is interpreted at all.

## Performing Updates/Installs

If an update is available for Galah-Installer, that update *must* be applied before any other updates.

The installer may need to perform a number of actions in order to perform an upgrade, and each step has a chance of failing. What we can't let happen is bring the system to the point where it is irrecoverable. If anything breaks in one of the installation scripts there needs to be mechanisms to either roll back the actions, resume where it left off, or somehow salvage things. This seems to necessitate the storage (and as a consequence, the serialization) of the state of the installation. This might not be as difficult as it seems though...

A typical installation from source will go along the lines of...

 1. Get source files (taken care of by the installer before the script runs)
 2. Build source files in some temporary directory.
 3. Ensure permissions are set correctly.
 3. Move source files into final destination (replacing anything that's there if we're upgrading).
 4. Ensuring symbolic links point to the right places and ld config is set up.

As long as I keep everything very self contained (in its own directory), failure shouldn't be too hard to handle. In fact, if anything fails during the entire process I described, we can just start over without issue.

Data migrations are much more dangerous, but a similar idea. Discrete steps, etc. These will be much harder to ensure the safety of, and the ability to do such depends on the database. More than likely, for most migrations, all other application that use the database will need to be brought down in order for the migration to occur safely.

### Package Information

A package that has been installed on the system has some basic information associated with it.

 * Configuration Directory: The configuration directory it uses.
 * Install Directory: The directory that contains all of its necessary binaries and libraries, should never change when not upgrading outside of any hot fixes (keeping track of such hot fixes can be part of the requirements in a later version of the installer).
 * Data Directory: The directory that contains any data the package manages (ex: database files). May be None/null.
 * Auxiliary Files: A dictionary mapping symbolic names of auxiliary files to lists of actual files or directories on the system. The meaning of each file is known only to the package's related scripts (install, migration, and controller). Init scripts would go in here for example.
 * Version: The installed version.

Deleting all of a packages configuration files, installation directory, and data directory should completely remove the package from the system (not including temporary files in /tmp). To make this easier, when packages are installed with shared libraries, they are not installed onto the system, but rather LD_LIBRARY_PATH is set instead (handled by the controller script).

The installer will also keep a number of pieces of meta-information for itself...

 * Managed: A boolean value indicating whether the package is managed by the installer.
 * Controller: The location of the controller script, which is responsible for starting up and shutting down the program. May be None/null if not applicable.

Extended information can be retrieved by getting the version info from the remote server (this can be done to ensure that no incompatible packages exist on the system still). The extended information may be cached, but it should always be pulled when possible because the list of compatible packages is likely to change.
