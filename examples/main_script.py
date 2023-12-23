
from hydroecolstm.utility.scaler import Scaler, get_scaler_name
from hydroecolstm.data.read_data import read_train_test_data, read_forecast_data
from hydroecolstm.data.read_config import read_config
from hydroecolstm.model.lstms import LSTM_DL
import matplotlib.pyplot as plt
import torch

#-----------------------------------------------------------------------------#
#                        Train and test model                                 #
#-----------------------------------------------------------------------------#

# Read configuration file
config = read_config("C:/Users/nguyenta/Documents/GitHub/HydroEcoLSTM/examples/config.yml")


# Read and split data
data = read_train_test_data(config)

# Scale data
x_scaler, y_scaler = get_scaler_name(config)

# Scale x_train
x_train_scaler, y_train_scaler = Scaler(), Scaler()
x_train_scaler.fit(x=data["x_train"], method=x_scaler)
x_train_scale = x_train_scaler.transform(x=data["x_train"])
x_test_scale = x_train_scaler.transform(x=data["x_test"])

y_train_scaler.fit(x=data["y_train"], method=y_scaler)
y_train_scale = y_train_scaler.transform(x=data["y_train"])
y_test_scale = y_train_scaler.transform(x=data["y_test"])

# Model
my_model = LSTM_DL(config=config)
model, y_predict = my_model.train(x_train=x_train_scale, y_train=y_train_scale)
y_test_scale_sim=my_model.forward(x_test_scale)


# Plot
for object_id in y_test_scale.keys():
    obs = y_test_scale[object_id].detach().numpy()
    sim = y_test_scale_sim[object_id].detach().numpy()
    plt.plot(sim[:,0], color = 'blue', label = "Simulated Q (train)", alpha=0.9, linewidth=0.75)
    plt.plot(obs[:,0], color = 'red', label = "Simulated Q (test)", alpha=0.9, linewidth=0.75)
    plt.title(label=f"object_id = {object_id}, target featue = {config['target_features'][0]}")
    plt.show()

#-----------------------------------------------------------------------------#
#                      Save model and load model                              #
#-----------------------------------------------------------------------------#
# Save model, save state_dict of the BASE MODEL
out_file = "C:/Users/nguyenta/Documents/save_model.pt"
torch.save(model.state_dict(), out_file)

# Load model
model_load = LSTM_DL(config=config)
model_load.model.load_state_dict(torch.load(out_file))
model_load.model.eval()

# Result with model retrieve from saved model should identical to model
y_test_scale_sim_load = model_load.forward(x_test_scale)

# Max min should be 0
for key in y_test_scale_sim.keys():
    print("Max diff = ", torch.max(y_test_scale_sim[key]-
                                   y_test_scale_sim_load[key]),
          " Min diff = ", torch.min(y_test_scale_sim[key]-
                                    y_test_scale_sim_load[key]))                                                                     

#-----------------------------------------------------------------------------#
#             Work with GUI, use the two lines below to call the GUI          #
#-----------------------------------------------------------------------------#
from hydroecolstm.interface.main_gui import show_gui
show_gui()
