from preprocess import *

# Constants for input and output locations
INPUT_DIR = '/home/users/jkleiss/TSI_C1'
OUTPUT_DIR = 'good_data'


def why_bad_images(timestamps, input_dir=INPUT_DIR):
	"""Returns four sets that self describe why a file in the given list is bad."""
	missing_mask = set()
	empty_mask = set()
	missing_image = set()
	empty_image = set()
	for time in timestamps:
		mask = extract_mask_path_from_time(time, input_dir)
		print("mask", mask)
		image = extract_img_path_from_time(time, input_dir)
		print("image", image)
		break
		if not os.path.isfile(mask):
			missing_mask.add(time)
		elif os.path.getsize(mask) == 0:
			empty_mask.add(time)
		print("I'm here")
		if not os.path.isfile(image):
			missing_image.add(time)
		elif os.path.getsize(image) == 0:
			empty_image.add(time)
	return missing_image, empty_image, missing_mask, empty_mask


def count_expected():
	"""Counts the number of unique timestamps we expect to simplify."""
	good_times = extract_data_from_csv("shcu_good_data.csv", "timestamp_utc")
	blacklist, bad_image, bad_mask = why_bad_images(good_times, INPUT_DIR)
	times = good_times - blacklist
	return len(times)


def count_blt():
	"""Counts the number of unique timestamps in the BLT input directory."""
	num_times = len(extract_all_times(INPUT_DIR, ['/SkyImage', '/CloudMask']))
	print("This is the number of files in Jessica's dir: ", num_times)
	return num_times


def count_actual():
	"""Counts the number of unique timestamps in the BLT target directory."""
	num_times = len(extract_all_times(OUTPUT_DIR, ['/simpleimage', '/simplemask']))
	print("This is the number of timestamps for which we simplify: ", num_times)
	return num_times


if __name__ == '__main__':
	good_times = extract_data_from_csv("shcu_good_data.csv", "timestamp_utc")
	missing_images, empty_images, missing_masks, empty_masks = why_bad_images(good_times)

	# for e in missing_images:
	# 	print(type(e))  # Just a sanity check. Expecting 'str'
	# 	break

	print("Writing to missing_images.txt. There are {} missing images".format(len(missing_images)))
	with open('missing_images.txt', 'w') as file:
		for time in missing_images:
			file.write(time + '\n')
		file.close()

	print("Writing to empty_images.txt. There are {} empty images".format(len(empty_images)))
	with open('empty_images.txt', 'w') as file:
		for time in empty_images:
			file.write(time + '\n')
		file.close()

	print("Writing to 'missing_masks.txt'. There are {} missing masks.".format(len(missing_masks)))
	with open('missing_masks.txt', 'w') as file:
		for time in missing_masks:
			file.write(time + '\n')
		file.close()

	print("Writing to 'empty_masks.txt'. There are {} empty masks.".format(len(empty_masks)))
	with open('empty_masks.txt', 'w') as file:
		for time in empty_masks:
			file.write(time + '\n')
		file.close()
