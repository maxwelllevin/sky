"""
Plots a comparison between network and the TSI measurements of fractional sky cover. Also compares both sources to
the Laser Ceilometer.

This script can be run after fsc_launch.py has finished.

This script requires four files: 'shcu_typical_data.csv', 'shcu_dubious_data.csv', 'typical_fsc.csv', and 'dubious_fsc.csv'.
* The 'shcu' files should be located in the typical_data/ and dubious_data/ directories.
* The 'fsc' files should be located in the RESULTS_DIR/EXPERIMENT_LABEL/ directory. This requirement should be satisfied
if the previous scripts have run successfully.

This script creates two plots and saves them as 'fsc_analyze_image_arscl.png' and 'fsc_rmse_barchart.png' in the
RESULTS_DIR/EXPERIMENT_LABEL/ directory. The 'fsc_analyze_image_arscl.png' plot is a set of scatter plots detailing how
fractional sky cover estimation sourced from our network-processed decision images relates to ARSCL ceilometer time -
averaged estimates of cloud fraction on typical and dubious data. These are plotted alongside fractional sky cover
estimates sourced from the total sky imager. The 'fsc_rmse_barchart.png' plot shows the root mean squared error for the
fractional sky cover obtained from the total sky imager and our network on typical and dubious data. Error is taken to
be the absolute value of the difference between fractional sky cover and cloud fraction.
"""

import pickle
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from utils import read_csv_file, extract_data_from_dataframe, extract_data_for_date_from_dataframe, load_pickled_file
from config import *

N_SAMPLES = 2500


def extract_arscl_and_image_fsc_from_dataframes(arscl_dataframe, image_dataframe, arscl_header="cf_tot", image_header="fsc_z"):
	"""Returns lists containing fractional sky cover obtained from two dataframes. Expects 'image_dataframe' to be a
	pandas dataframe with a header for 'fsc_z' and expects 'arscl_dataframe' to be a pandas dataframe with a header
	for 'cf_tot'. Expects both dataframes to have a header for 'timestamp_utc'. Additionally expects the dataframes to
	be clean in the aforementioned categories. I.e. NaN values are not permitted. Please us df.dropna() or some other
	method to handle missing values."""
	image_times = set(extract_data_from_dataframe(image_dataframe, "timestamp_utc"))
	arscl_times = set(extract_data_from_dataframe(arscl_dataframe, "timestamp_utc"))
	times = image_times.intersection(arscl_times)  # Necessary to correct for missing times
	x, y, residual, residual1 = [], [], [], []
	mse = 0
	for t in times:
		x.append(extract_data_for_date_from_dataframe(arscl_header, t, arscl_dataframe))
		y.append(extract_data_for_date_from_dataframe(image_header, t, image_dataframe))
		mse += (y[-1] - x[-1]) ** 2
		residual.append(abs(y[-1] - x[-1]))
		residual1.append(y[-1] - x[-1])
	return x, y, (mse / len(times)) ** 0.5, np.array(residual), np.array(residual1)


def residual_to_quartiles(residual):
	"""Sorts a list of residual errors and returns the 25th and 75th quartiles."""
	residual = sorted(list(residual))
	q25 = residual[int(0.25 * len(residual))]
	q50 = residual[int(0.50 * len(residual))]
	q75 = residual[int(0.75 * len(residual))]
	return q25, q50, q75


def scatter_plot(scatter, name, ylabel, title, xlabel):
	"""Makes a plot with the given parameters"""
	plt.title(title)
	plt.xlabel(xlabel)
	plt.ylabel(ylabel)
	plt.scatter(scatter[0], scatter[1], s=0.5)
	plt.plot([0, 1], [0, 1], c='orange', lw=2)
	plt.savefig(RESULTS_DIR + '/' + EXPERIMENT_LABEL + name, dpi=300)
	plt.close()


if __name__ == "__main__":

	# Reads data from shcu_typical_data.csv, takes a sample of the times, and gets data for plotting
	typical_arscl_dataframe = read_csv_file(TYPICAL_DATA_CSV)  # Contains both ARSCL and TSI Data
	typical_arscl_dataframe = typical_arscl_dataframe.dropna(subset=['fsc_z', 'cf_tot', 'timestamp_utc'])
	typical_times = load_pickled_file(TYPICAL_VALID_FILE)
	typical_times = typical_times[0:N_SAMPLES]
	typical_arscl_dataframe = typical_arscl_dataframe[typical_arscl_dataframe['timestamp_utc'].isin(typical_times)]
	typical_arscl_tsi = extract_arscl_and_image_fsc_from_dataframes(typical_arscl_dataframe, typical_arscl_dataframe)

	# Reads data from shcu_dubious_data.csv, takes a sample of the times, and gets data for plotting
	dubious_arscl_dataframe = read_csv_file(DUBIOUS_DATA_CSV)  # Contains both ARSCL and TSI Data
	dubious_arscl_dataframe = dubious_arscl_dataframe.dropna(subset=['fsc_z', 'cf_tot', 'timestamp_utc'])
	dubious_times = load_pickled_file(DUBIOUS_VALID_FILE)  # Change this to TEST_FILE for final plotting.
	dubious_times = dubious_times[0:N_SAMPLES]
	dubious_arscl_dataframe = dubious_arscl_dataframe[dubious_arscl_dataframe['timestamp_utc'].isin(dubious_times)]
	dubious_arscl_tsi = extract_arscl_and_image_fsc_from_dataframes(dubious_arscl_dataframe, dubious_arscl_dataframe)

	# Reads data from typical_fsc.csv and uses the times sample from shcu_typical_data.csv to get data for plotting
	typical_network_dataframe = read_csv_file(RESULTS_DIR + '/' + EXPERIMENT_LABEL + '/typical_fsc.csv')  # Contains NETWORK Data
	typical_network_dataframe = typical_network_dataframe.dropna(subset=['fsc_z', 'timestamp_utc'])
	typical_network_dataframe = typical_network_dataframe[typical_network_dataframe['timestamp_utc'].isin(typical_times)]
	typical_arscl_network = extract_arscl_and_image_fsc_from_dataframes(typical_arscl_dataframe, typical_network_dataframe)

	# Reads data from dubious_fsc.csv and uses the times sample from shcu_dubious_data.csv to get data for plotting
	dubious_network_dataframe = read_csv_file(RESULTS_DIR + '/' + EXPERIMENT_LABEL + '/dubious_fsc.csv')  # Contains NETWORK Data
	dubious_network_dataframe = dubious_network_dataframe.dropna(subset=['fsc_z', 'timestamp_utc'])
	dubious_network_dataframe = dubious_network_dataframe[dubious_network_dataframe['timestamp_utc'].isin(dubious_times)]
	dubious_arscl_network = extract_arscl_and_image_fsc_from_dataframes(dubious_arscl_dataframe, dubious_network_dataframe)

	# Gets comparison data for TSI and Network decision images on typical and dubious data
	typical_tsi_network = extract_arscl_and_image_fsc_from_dataframes(typical_arscl_dataframe, typical_network_dataframe, arscl_header="fsc_z")
	dubious_tsi_network = extract_arscl_and_image_fsc_from_dataframes(dubious_arscl_dataframe, dubious_network_dataframe, arscl_header="fsc_z")

	# Typical/Dubious Data FSC vs CF Plots for TSI and Network Decision Images
	titles = ['Typical Data', 'Dubious Data']
	ylabels = ['FSC (TSI)', 'FSC (Network)']
	xlabels = ['Ceilometer CF'] * 2
	data = [typical_arscl_tsi, dubious_arscl_tsi, typical_arscl_network, dubious_arscl_network]
	fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(14, 9), sharey=True, sharex=True)
	for ax, col in zip(axes[0], titles):
		ax.set_title(col, fontsize=30)
	for ax, row in zip(axes[:, 0], ylabels):
		ax.set_ylabel(row, fontsize=26)
	for ax, col in zip(axes[-1], xlabels):
		ax.set_xlabel(col, fontsize=26)
	for i, ax in enumerate(axes.ravel()):
		ax.tick_params(labelsize='x-large')
		ax.scatter(data[i][0], data[i][1], s=50, alpha=0.3)
		ax.plot([0, 1], [0, 1], lw=4, color='orange')
	fig.tight_layout()
	fig.savefig(RESULTS_DIR + '/' + EXPERIMENT_LABEL + "/fsc_analyze_image_arscl.png")
	# plt.show()

	# RMSE plot
	# data to plot
	n_groups = 2
	tsi_rsme = (typical_arscl_tsi[2], dubious_arscl_tsi[2])
	network_rsme = (typical_arscl_network[2], dubious_arscl_network[2])
	fig = plt.figure(figsize=(12, 9))
	index = np.arange(n_groups)
	bar_width = 0.3
	ax = fig.add_subplot(111)
	ax.tick_params(labelsize='x-large')
	ax.bar(index, tsi_rsme, bar_width, label='TSI')
	ax.bar(index + bar_width, network_rsme, bar_width, color='orange', label='Network')
	# plt.yticks(fontsize=20)
	plt.ylabel('Root Mean Squared Error', fontsize=26)
	plt.title('Fractional Sky Cover RMSE', fontsize=30)
	ax.tick_params(
		axis='x',  # changes apply to the x-axis
		which='both',  # both major and minor ticks are affected
		bottom=False,  # ticks along the bottom edge are off
		top=False,  # ticks along the top edge are off
		labelbottom=True)
	plt.xticks((index + bar_width / 2), ('Typical Data', 'Dubious Data'), fontsize=26)
	ax.legend(fontsize=20)
	fig.savefig(RESULTS_DIR + "/" + EXPERIMENT_LABEL + "/fsc_rmse_barchart.png")
