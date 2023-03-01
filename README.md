# Sphinx Simple Version

Simply manage multiple sphinx documentation versions.

## Installation

Specify it as a requirement in your `requirements.txt`. We do not publish the
extension to PyPi, so we have to install it using Git. Since the extension is so
simple, you could also copy the code to your local project and skip the
requirement.

```
sphinx_simpleversion @ git+https://github.com/isaksamsten/sphinx_simpleversion.git@main
```

Then we have to specify the extension in our Sphinx configuration file,
`conf.py`:

```python
extensions = [
    "sphinx_simpleversion",
]

versions_develop_branch = "main"
versions_include_branch_pattern = r"(?P<version>\d+.\d+).X"
```

Now your templates have the following context variable:

```
versions.versions        # list of Version-objects
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

For example, you could list the installed versions with:

```jinja
{%- if versions %}
<ul>
  <li>
    <strong>Versions</strong>
    <ul>
      {%- for item in versions.versions %}
        {%- if not item.is_current %}
            <li>
                <a href="{{ item.url }}">{{ item.name }}</a>
            </li>
        {%- else %}
            <li>{{ item.name }}</li>
        {%- endif %}
      {%- endfor %}
    </ul>
  </li>
</ul>
{%- endif %}
```

Or setup warnings if the user is reading an old or development version of the
documentation:

```jinja
{% if versions and versions.current_version != versions.stable_version %}
<div>
{% if versions.current_version.is_released %}
    You're reading an old version of this documentation. If you want
    up-to-date information, please have a look at
    <a href="{{ versions.stable_version.url }}">{{versions.stable_version.name}}</a>.
{% else %}
    You're reading the documentation for a development version.
    For the latest released version, please have a look at
    <a href="{{ versions.stable_version.url }}">{{versions.stable_version.name}}</a>.
{% endif %}
</div>
{% endif %}
```

## Configuration options

`versions_develop_branch`

: (`str`) The main develop branch where documentation is also built. This
release will be marked with is_release=False, unless its the only documentation
we build.

`versions_include_branch_pattern`

: (`str`, regular expression) The other branches that will have documentation
built for them. We need to specify one part of the regular expression as
`(?P<version>)` to extract the version name. By default, the included branches
follow the naming convention of `{major}.{minor}.X`.

## Github Actions example

Here we provide a sample configuration to build and deploy the documentation of
the `main`, `1.1.X` and `1.0.X` branches of our project to `gh-pages` of a
Github repository. The build declaration specify that the build will be pushed
to subdirectories with names corresponding to the branch names. So after build,
the `gh-pages` branch will have the following layout:

```
├── main
│   └── index.html
├── 1.1.X
│   ├── other.html
│   └── index.html
└── 1.1.0
    └── index.html
```

We repeatedly build the documentation for the specified branches, and for each
branch `sphinx_simpleversion` collects information about the other branches we
build so that we can include links to those from each of the documentations.

We also define that the build should be triggered by pushes to any of the
documentation branches, but this is not required. You could for example, only
build documentation on pushes to the `main` branch.

```yaml
name: Build, test and upload to PyPI

on:
  push:
    branches:
      - main
      - 1.0.X
      - 1.1.X

build_docs:
runs-on: ubuntu-latest
strategy:
    fail-fast: true
    max-parallel: 1
    matrix:
    branch: [main, 1.1.X, 1.0.X]

steps:
    - uses: actions/checkout@v3
    with:
        fetch-depth: 0
        ref: ${{ matrix.branch }}

    - uses: actions/setup-python@v4
    name: Install Python
    with:
        python-version: "3.9"

    - name: Install requirements
    run: |
        python -m pip install --upgrade pip
        python -m pip install -r requirements.txt

    - name: Install current version
    run: pip install --force-reinstall .

    - name: Build docmentation
    run: |
        mkdir html
        python -I -m sphinx . html

    - name: Deploy documentation
    uses: peaceiris/actions-gh-pages@v3
    with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./html
        destination_dir: ${{ matrix.branch }}
```

What is left, is to manually specify an `index.html` in the root of `gh-pages`.
For example:

```html
<!DOCTYPE html>
<html>
  <head>
    <title>Redirecting to main branch</title>
    <meta charset="utf-8" />
    <meta http-equiv="refresh" content="0; url=./main/index.html" />
    <link
      rel="canonical"
      href="https://your-github-name.github.io/main/index.html"
    />
  </head>
</html>
```

## Anyone using it?

Just me. Here is an example:

- https://github.com/wildboar-foundation/wildboar
