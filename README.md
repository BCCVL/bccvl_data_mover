bccvl_data_mover
================

Data Mover API for BCCVL

### Developer Setup

    git clone https://github.com/BCCVL/bccvl_data_mover.git
    cd bccvl_data_mover
    virtualenv --no-site-packages venv
    cd venv/bin; source activate; cd ../..
    easy_install pyramid WebTest nose
    easy_install pyramid_xmlrpc

**Start server**

    python src/org/bccvl/data_mover/application.py
    
