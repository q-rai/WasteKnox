# Getting Started


1. Install anaconda -- version doesn't matter

2. Import anaconda environment: `conda env create -n hackathon -f hackathon.yml`

3. Switch to the new environment: `source activate hackathon`

4. Add the environment to your jupyter: `python -m ipykernel install --user --name hackathon --display-name "Hackathon"`. 



# Production

```
bokeh serve --show visualization
```
