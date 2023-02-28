# Sphinx Simple Version

Manage multiple sphinx documentation versions simply. Using git.

`conf.py`

```python
extensions = [
    "sphinx_simpleversion",
]

versions_develop_branch = "main"

# Version branches are named 1.0.X, 2.1.X etc
versions_include_branch_pattern = r"(?P<version>\d+.\d+).X"
#                                    |----------|
#                                          \- (required) named pattern to extract the version name
```

Now your templates have the following context variable:

```
versions.versions        # list of Version objects
versions.current_version # Version-object
versions.stable_version  # Version-object
```

Version-object:

```
version.is_release  # True if version is from the develop_branch
version.is_current  # True if version is from the current branch
version.name        # Name of the version, as extracted by the regex
version.url_base    # The url_base, same as branch
version.url         # url_base/index.html
```
