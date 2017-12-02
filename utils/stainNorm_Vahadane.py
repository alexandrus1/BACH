"""
Uses the spams package:

http://spams-devel.gforge.inria.fr/index.html

Use with python via e.g https://anaconda.org/conda-forge/python-spams
"""

import cv2 as cv
import numpy as np
import spams


def remove_zeros(I):
    """
    Remove zeros
    :param I:
    :return:
    """
    mask = (I == 0)
    I[mask] = 1
    return I


def RGB_to_OD(I):
    """

    :param I:
    :return:
    """
    I = remove_zeros(I)
    return -1 * np.log(I / 255)


def OD_to_RGB(OD):
    """

    :param OD:
    :return:
    """
    return (255 * np.exp(-1 * OD)).astype(np.uint8)


def normalize_rows(A):
    """
    Normalize rows of an array
    :param A:
    :return:
    """
    return A / np.linalg.norm(A, axis=1)[:, None]


def notwhite_mask(I, thresh=0.8):
    """
    Get a binary mask where true denotes 'not white'
    :param I:
    :param thresh:
    :return:
    """
    I_LAB = cv.cvtColor(I, cv.COLOR_RGB2LAB)
    L = I_LAB[:, :, 0] / 255.0
    return (L < thresh)


def sign(x):
    """
    Returns the sign of x
    :param x:
    :return:
    """
    if x > 0:
        return +1
    elif x < 0:
        return -1
    elif x == 0:
        return 0


def enforce_rows_positive(X):
    """
    Make rows positive if possible. Return is tuple of X and bool (true if success)
    :param X:
    :return:
    """
    n, l = X.shape
    for i in range(n):
        sign0 = sign(X[i, 0])
        for j in range(1, l):
            if sign(X[i, j]) != sign0:
                print('Mixed sign rows.')
                return X, False
        X[i] = sign0 * X[i]
    return X, True


def get_stain_matrix(I, threshold=0.8, sub_sample=10000):
    """

    :param I:
    :param threshold:
    :param sub_sample:
    :return:
    """
    mask = notwhite_mask(I, thresh=threshold).reshape((-1,))
    OD = RGB_to_OD(I).reshape((-1, 3))
    OD = OD[mask]
    n = OD.shape[0]
    if n > sub_sample:
        OD = OD[np.random.choice(range(n), sub_sample)]
    dictionary = spams.trainDL(OD.T, K=2, lambda1=.1, mode=2, modeD=0, posAlpha=True, posD=True).T
    print(dictionary.shape)
    if dictionary[0, 0] < dictionary[1, 0]:
        dictionary = dictionary[[1, 0], :]
    dictionary = normalize_rows(dictionary)
    return dictionary


def get_coeffs(I, stain_matrix):
    """

    :param I:
    :param stain_matrix:
    :return:
    """
    OD = RGB_to_OD(I).reshape((-1, 3))
    return spams.lasso(OD.T, D=stain_matrix.T, mode=2, lambda1=.1, pos=True).toarray().T


def normalize_Vahadane(patch, targetImg):
    """

    :param patch:
    :param targetImg:
    :return:
    """
    stain_matrix_source = get_stain_matrix(patch)
    stain_matrix_target = get_stain_matrix(targetImg)
    source_concentrations = get_coeffs(patch, stain_matrix_source)
    return 255 * np.exp(-1 * np.dot(source_concentrations, stain_matrix_target).reshape(patch.shape))