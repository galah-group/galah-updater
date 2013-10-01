# gicore
import errors

def _versions_between(lst, a, b):
    """
    Returns the items between two items in a list.

    .. code-block:: python

        >>> my_list = [1, 2, 3, 4]
        >>> _versions_between(my_list, 1, 3)
        [2, 3]
        >>> _versions_between(my_list, 3, 1)
        [2, 1]

    :param lst: The list.
    :param a: The first item to look for, will not appear in the resulting
            list.
    :param b: The second item to look for, will appear in the resulting list.

    :returns: A list.

    .. note::

        This function was explicitly designed for use by determine_preactions()
        and should not be used anywhere else, as the implementation may change
        (or it may even disappear entirely).

    """

    a_index = lst.index(a)
    b_index = lst.index(b)
    if a_index < b_index:
        return [lst[i] for i in xrange(a_index + 1, b_index + 1)]
    else:
        return [lst[i] for i in reversed(xrange(b_index, a_index))]

class UAInstall(object):
    "An unresolved install action."

    def __init__(self, name, version):
        self.name = name
        self.version = version

    def __repr__(self):
        return "UAInstall(name = %s, version = %s)" % (self.name, self.version)

    def __eq__(self, other):
        return self.name == other.name and self.version == other.version

class UAMigrate(object):
    "An unresolved migrate action."

    def __init__(self, name, to_version, from_version):
        self.name = name
        self.to_version = to_version
        self.from_version = from_version

    def __repr__(self):
        return "UAMigrate(name = %s, to_version = %s, from_version = %s)" % (
            self.name, self.to_version, self.from_version)

    def __eq__(self, other):
        return (self.name == other.name and
            self.to_version == other.to_version and
            self.from_version == other.from_version)

def determine_preactions(all_packages, installed_packages, desired_state):
    """
    Determines at the highest level what needs to be done in order to reach a
    given state in terms of migrations and installations.

    This function returns a list of "unresolved actions" which may or may not
    need to be performed. Each action will require a remote query to resolve
    into concrete actions that can actually be carried out on the machine.

    .. note::

        The return value is guaranteed to order packages based on their
        lexigraphic ordering.

    :param all_packages: A dictionary mapping package names to a list of
            versions that we can potentially install.
    :param installed_packages: A dictionary mapping package names to
            strings representing the current installed version.
    :param desired_state: A dictionary mapping package names to strings
            representing the desired installed version.

    :returns: A list of "unresolved actions".

    """

    actions = []
    ordered_keys = sorted(desired_state.keys())
    for name, version in ((k, desired_state[k]) for k in ordered_keys):
        if name in installed_packages and name not in all_packages:
            raise errors.CriticalError(
                "An installed package is not listed in the package listing "
                "pulled from the remote server."
            )
        if name not in all_packages:
            raise ValueError("%s is not a supported package." % (name, ))
        if installed_packages.get(name) == "UNMANAGED":
            raise ValueError("%s is not managed by this installer." % (name, ))
        if installed_packages[name] not in all_packages[name]:
            raise ValueError(
                "The installed package %s version %s is not in the package "
                "index." % (name, installed_packages[name])
            )
        if version not in all_packages[name]:
            raise ValueError(
                "Cannot install package %s version %s. Not in package "
                "index." % (name, installed_packages[name])
            )

        if name in installed_packages:
            from_version = installed_packages[name]
            for i in _versions_between(all_packages[name],
                    installed_packages[name], version):
                actions.append(UAMigrate(
                    name = name,
                    from_version = from_version,
                    to_version = i
                ))
                from_version = i
        actions.append(UAInstall(
            name = name,
            version = version
        ))
    return actions
