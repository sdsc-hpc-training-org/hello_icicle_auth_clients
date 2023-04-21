echo "###CHECKING FOR UPDATES TO PYTHON DEPENDENCIES###"
pip install --upgrade build
pip install --upgrade twine

echo "###BUILDING PACKAGE###"
python -m build .

echo "###UPLOADING###"
python3 -m twine upload --skip-existing --repository testpypi dist/*
