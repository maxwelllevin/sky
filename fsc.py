import sys
from utils import *
from config import *


def find_center(mask):
	"""Returns the center of the locations of the first and last non-black pixels and the difference in height
	between them. Returns the center (y, x) and the average radius."""
	top, bottom, left, right = find_circle_boundary(mask)
	vertical_radius = (bottom - top) / 2
	horizontal_radius = (right - left) / 2
	return ((top + bottom) / 2, (left + right) / 2), (vertical_radius + horizontal_radius) / 2


def find_circle_boundary(mask):
	"""Finds the first non-black pixel in all cardinal directions."""
	answer = []
	flag = False
	for i in range(mask.shape[0]):  # Top
		if flag:
			break
		for j in range(mask.shape[1]):
			if tuple(mask[i, j]) != (0, 0, 0):
				answer += [i]
				flag = True
				break
	flag = False
	for i in range(mask.shape[0] - 1, -1, -1):  # Bottom
		if flag:
			break
		for j in range(mask.shape[1]):
			if tuple(mask[i, j]) != (0, 0, 0):
				answer += [i]
				flag = True
				break
	flag = False
	for j in range(mask.shape[1]):  # Left
		if flag:
			break
		for i in range(mask.shape[0]):
			if tuple(mask[i, j]) != (0, 0, 0):
				answer += [j]
				flag = True
				break
	flag = False
	for j in range(mask.shape[1] - 1, -1, -1):  # Right
		if flag:
			break
		for i in range(mask.shape[0]):
			if tuple(mask[i, j]) != (0, 0, 0):
				answer += [j]
				flag = True
				break
	return answer


def get_fsc(mask, threshold=0.645):
	"""Computes the fractional sky cover from a given mask. By default, computes these values in the zenith region.
	Specify zenith ratio by changing threshold between 0 and 1. Returns total sky cover, opaque sky cover,
	thin sky cover."""
	sky_pixels = 0
	cloud_pixels = 0
	thin_pixels = 0
	t, b, l, r = find_circle_boundary(mask)
	center, rad = find_center(mask)
	new_r = threshold * rad
	for i in range(t, b + 1):
		for j in range(l, r + 1):
			if (i - center[0]) ** 2 + (j - center[1]) ** 2 > new_r ** 2:
				# mask[i, j] = [0, 0, 0] # Uncomment this to show the portion used to calculate fsc
				continue
			color = tuple(mask[i, j])
			if color == (0, 0, 0) or color == (0, 255, 0):
				continue
			elif color == (0, 0, 255):
				sky_pixels += 1
			elif color == (255, 255, 255):
				cloud_pixels += 1
			else:
				thin_pixels += 1
	total = sky_pixels + cloud_pixels + thin_pixels
	return (cloud_pixels + thin_pixels) / total, thin_pixels / total, cloud_pixels / total


def get_fsc_from_file(filename):
	"""Computes the fractional sky cover given a filename that leads to a sky mask."""
	if "simplemask" in filename:
		mask = get_simple_mask(extract_timestamp(filename))
		return get_fsc(mask)
	elif "networkmask" in filename:
		mask = get_network_mask_from_time_and_label(extract_timestamp(filename), extract_exp_label(filename))
		return get_fsc(mask)


def fsc(input_data_file, output_data_csv):
	if USE_VALID_FSC:
		times = load_pickled_file(input_data_file)
	else:
		times = sorted(list(extract_data_from_csv(input_data_file, 'timestamp_utc')))
	spacing = int(len(times)/100)
	with open(RESULTS_DIR + '/' + EXPERIMENT_LABEL + '/' + output_data_csv, 'w') as f:
		f.write("timestamp_utc,fsc_z,fsc_thn_z,fsc_opq_z" + "\n")
		count = 0
		for t in times:
			if count % spacing == 0:
				print("progress: " + str(round(count/spacing)) + "%")
				f.flush()
			if os.path.isfile(extract_network_mask_path_from_time(t, EXPERIMENT_LABEL)):
				fsc_z, fsc_thn_z, fsc_opq_z = get_fsc_from_file(extract_network_mask_path_from_time(t, EXPERIMENT_LABEL))
				f.write("{},{},{},{}".format(t, fsc_z, fsc_thn_z, fsc_opq_z) + "\n")
			count += 1
		f.flush()
		print("progress: 100%")


if __name__ == '__main__':
	INPUT_DATA_FILE = sys.argv[1]
	OUTPUT_DATA_CSV = sys.argv[2]
	fsc(INPUT_DATA_FILE, OUTPUT_DATA_CSV)
