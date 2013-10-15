from mangoengine import *

class AllPackages(Model):
    packages = DictField(
        of_key = StringField(),
        of_value = ListField(of = StringField)
    )

class VersionInfo(Model):
    name = StringField()
    version = StringField()
    compatible_with = DictField(
        of_key = StringField(),
        of_value = ListField(of = StringField()),
        serialized_name = "compatible-with"
    )
    require_offline = ListField(of = StringField,
        serialized_name = "require-offline")
    migrations = ListField(of = StringField(), nullable = True)
    installer_mirrors = ListField(of = StringField(),
        serialized_name = "installer-mirrors")
    archive_mirrors = ListField(of = StringField(),
        serialized_name = "archive-mirrors", nullable = True)
    migration_mirrors = ListField(of = StringField(),
        serialized_name = "migration-mirrors", nullable = True)

class AllInstalledListing(Model):
    packages = DictField()

class InstalledPackage(Model):
    name = StringField()
    version = StringField()
    compatible_with = DictField(
        of_key = StringField(),
        of_value = ListField(of = StringField()),
        serialized_name = "compatible-with"
    )
    configuration_dir = StringField(serialized_name = "configuration-dir")
    install_dir = StringField(serialized_name = "install-dir")
    data_dir = StringField(serialized_name = "data-dir")
    auxiliary_files = ListField(of = StringField(),
        serialized_name = "auxiliary-files")
    controller_dir = StringField(serialized_name = "controller-dir")
