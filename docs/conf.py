# pylint: skip-file
# documentation build configuration file
import os
import pathlib
import re
import shutil
import subprocess
import sys
import warnings

from sh.contrib import git

PROJECT_ROOT = pathlib.Path(__file__).expanduser().resolve().parent.parent
CURR_PATH = PROJECT_ROOT / "docs"
DOX_DIR = PROJECT_ROOT / "doxygen"


def run_doxygen():
    """Run the doxygen make command in the designated folder."""
    tmpdir = CURR_PATH / "tmp"
    if tmpdir.exists():
        shutil.rmtree(tmpdir)
    else:
        tmpdir.mkdir()
    try:
        if not DOX_DIR.exists():
            DOX_DIR.mkdir()
        os.chdir(os.path.join(PROJECT_ROOT, DOX_DIR))
        subprocess.run(
            ["cmake", "..", "-DBUILD_DOXYGEN=ON", "-GNinja"], check=True, cwd=DOX_DIR
        )
        subprocess.run(["ninja", "tl2cgen_doc_doxygen"], check=True, cwd=DOX_DIR)
        shutil.copytree(DOX_DIR / "doc_doxygen" / "html", tmpdir / "dev")
    except OSError as e:
        raise RuntimeError(f"Doxygen execution failed {str(e)}") from e


def is_readthedocs_build():
    if os.environ.get("READTHEDOCS", None) == "True":
        return True
    warnings.warn(
        "Skipping Doxygen build... You won't have documentation for C/C++ functions. "
        "Set environment variable READTHEDOCS=True if you want to build Doxygen. "
        "(If you do opt in, make sure to install Doxygen, Graphviz, CMake, and C++ compiler "
        "on your system.)"
    )
    return False


if is_readthedocs_build():
    run_doxygen()


git_branch_env = os.getenv("SPHINX_GIT_BRANCH", default=None)
if not git_branch_env:
    # If SPHINX_GIT_BRANCH environment variable is not given, run git
    # to determine branch name
    git_branch = [
        re.sub(r"origin/", "", x.lstrip(" "))
        for x in str(git.branch("-r", "--contains", "HEAD")).rstrip("\n").split("\n")
    ]
    git_branch = [x for x in git_branch if "HEAD" not in x]
else:
    git_branch = [git_branch_env]
print(f"git_branch = {git_branch[0]}")

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
libpath = PROJECT_ROOT / "python"
sys.path.insert(0, str(libpath))
sys.path.insert(0, str(CURR_PATH))

# -- General configuration ------------------------------------------------

# General information about the project.
project = "TL2cgen"
author = f"{project} developers"
copyright = f"2023, {author}"
github_doc_root = "https://github.com/dmlc/tl2cgen/tree/mainline/docs/"

os.environ["TL2CGEN_BUILD_DOC"] = "1"
# Version information.
with open(PROJECT_ROOT / "python" / "tl2cgen" / "VERSION", "r", encoding="utf-8") as f:
    version = f.read().rstrip()
release = version

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom ones
extensions = [
    "matplotlib.sphinxext.plot_directive",
    "sphinxcontrib.jquery",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.mathjax",
    "sphinx.ext.intersphinx",
    "sphinx_gallery.gen_gallery",
    "breathe",
    "autodocsumm",
]

sphinx_gallery_conf = {
    # path to your example scripts
    "examples_dirs": [],
    # path to where to save gallery generated output
    "gallery_dirs": [],
    "matplotlib_animations": True,
}

autodoc_typehints = "description"

autodoc_default_options = {
    "autosummary": True,
}

graphviz_output_format = "png"
plot_formats = [("svg", 300), ("png", 100), ("hires.png", 300)]
plot_html_show_source_link = False
plot_html_show_formats = False

# Breathe extension variables
breathe_projects = {}
if is_readthedocs_build():
    breathe_projects = {
        "tl2cgen": os.path.join(PROJECT_ROOT, DOX_DIR, "doc_doxygen/xml")
    }
breathe_default_project = "tl2cgen"

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
source_suffix = [".rst", ".md"]

# The encoding of source files.
# source_encoding = 'utf-8-sig'

# The master toctree document.
master_doc = "index"

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = "en"

autoclass_content = "both"

# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
# today = ''
# Else, today_fmt is used as the format for a strftime call.
# today_fmt = '%B %d, %Y'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ["_build"]
html_extra_path = []
if is_readthedocs_build():
    html_extra_path = [os.path.join(CURR_PATH, "tmp")]

# The reST default role (used for this markup: `text`) to use for all
# documents.
# default_role = None

# If true, '()' will be appended to :func: etc. cross-reference text.
# add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
# add_module_names = True

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
# show_authors = False

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# A list of ignored prefixes for module index sorting.
# modindex_common_prefix = []

# If true, keep warnings as "system message" paragraphs in the built documents.
# keep_warnings = False

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = False

# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = "sphinx_rtd_theme"
html_theme_options = {"logo_only": False}

html_css_files = ["css/custom.css"]

html_sidebars = {"**": ["logo-text.html", "globaltoc.html", "searchbox.html"]}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# Output file base name for HTML help builder.
htmlhelp_basename = project + "doc"

# -- Options for LaTeX output ---------------------------------------------
latex_elements = {}  # type: ignore

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, f"{project}.tex", project, author, "manual"),
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3.8", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "scipy": ("https://docs.scipy.org/doc/scipy/", None),
    "pandas": ("https://pandas.pydata.org/pandas-docs/stable/", None),
    "sklearn": ("https://scikit-learn.org/stable", None),
    "treelite": ("https://treelite.readthedocs.io/en/latest/", None),
}


def setup(app):
    app.add_css_file("custom.css")
