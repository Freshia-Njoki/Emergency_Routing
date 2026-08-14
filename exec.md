python run_full_framework.py

cd "/d/MSc - Route optimisation for road traffic evasion/Routing App"
source venv/Scripts/activate

which python

python -c "import numpy, scipy, pandas, networkx, shapely; print('all ok')"

python -m src.evaluation.evaluate_framework --sliding-window --model-dir models/saved --data-dir data --results-dir results/sliding


python -c "
import pickle, numpy as np
d = pickle.load(open('models/saved/training_history.pkl','rb'))
print('Final training loss (MSE):    ', round(d['loss'][-1], 4))
print('Best validation loss (MSE):   ', round(min(d['val_loss']), 4))
print('Final training MAE:           ', round(d['mae'][-1], 4))
print('Best validation MAE:          ', round(min(d['val_mae']), 4))
print('Epochs trained:               ', len(d['loss']))
print('Best epoch (lowest val_loss): ', d['val_loss'].index(min(d['val_loss']))+1)
"