#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Finds the zenith area of TSI skymasks
"""

import numpy as np
from PIL import Image
from scipy import misc


def get_mask(timestamp):
	""" Returns the mask of a given timestamp in the simplemask data directory. Does not handle exceptions."""
	return np.array(misc.imread('data/simplemask/simplemask' + str(timestamp) + '.png')) #TODO: Look into reading this as a uint8 image


def show_skymask(timestamp=None, mask=None):
	""" Shows the mask for a given timestamp, alternatively can show a given mask."""
	if mask is not None:
		mask = get_mask(timestamp)
	mask_image = Image.fromarray(mask.astype('uint8'))
	mask_image.show()


def find_first_non_black_pixel(timestamp, mask=None):
	""" Finds the location of the first non-black pixel in the mask, vertically."""
	if mask is not None:
		mask = get_mask(timestamp)
	for i in range(mask.shape[0]):
		for j in range(mask.shape[1]):
			if tuple(mask[i, j]) != (0, 0, 0):
				return i, j


def find_last_non_black_pixel(timestamp, mask=None):
	""" Finds the location of the last non-black pixel in the mask, vertically."""
	if mask is not None:
		mask = get_mask(timestamp)
	for i in range(mask.shape[0] - 1, -1, -1):
		for j in range(mask.shape[1]):
			if tuple(mask[i, j]) != (0, 0, 0):
				return mask.shape[0] - 1 - i, j #TODO: Check if this is off by 1 pixel


def find_center(timestamp, mask=None):
	""" Returns the center of the locations of the first and last non-black pixels and the difference in
	height between them."""
	p1 = find_first_non_black_pixel(timestamp, mask)
	p2 = find_last_non_black_pixel(timestamp, mask)
	return ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2), (p2[0] - p1[0]) / 2


def get_pixels_in_center(timestamp, mask=None, threshold=0.6):
	""" Returns a new image mask containing pixels that are within a threshold of the center of the mask."""
	center, r = find_center(timestamp, mask)
	new_r = threshold * r
	new_mask = mask.copy()
	for i in range(mask.shape[0]):
		for j in range(mask.shape[1]):
			if (i - center[0]) ** 2 + (j - center[1]) ** 2 > new_r ** 2:
				new_mask[i, j] = [0, 0, 0]
	return np.array(new_mask)


# TODO: Make this more efficient by not looping through all pixels & not duplicating mask
def get_fsc(mask):
	""" Computes the fractional sky cover from a given mask. Returns total sky cover, opaque sky cover."""
	sky_pixels = 0
	cloud_pixels = 0
	thin_pixels = 0
	for i in range(mask.shape[0]):
		for j in range(mask.shape[1]):
			color = tuple(mask[i, j])
			if color == (0, 0, 0):
				continue
			elif color == (0, 0, 255):
				sky_pixels += 1
			elif color == (0, 255, 0):
				continue
			elif color == (255, 255, 255):
				cloud_pixels += 1
			else:
				thin_pixels += 1
	total = sky_pixels + cloud_pixels + thin_pixels
	return (cloud_pixels + thin_pixels) / total, cloud_pixels / total


# for index, x in np.ndenumerate(mask):
#
# #black = 3
#
# # top
# for i in np.nditer():
#     if
#
#         img = misc.imread('simplemask/' + file)
#         b_mask[(img != color).any(axis=2)] = BLUE


# preproccess.py simplify_all_masks to get all skymasks

if __name__ == '__main__':
	timestamp = 20160414162830
	mask = get_mask(timestamp)
	new_mask = get_pixels_in_center(timestamp, mask)
	fsc = get_fsc(new_mask)
	show_skymask(mask=mask)
	show_skymask(mask=new_mask)
	print(fsc)

