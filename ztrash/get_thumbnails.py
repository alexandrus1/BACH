import os
from utils import misc_utils as mu

### change me ###
root_dir = '/media/peter/HDD 1/ICIAR2018_BACH_Challenge/'

###

data_dir = root_dir + 'Photos'
save_dir = root_dir + 'BACH_thumbnails'

classes = ('Benign', 'InSitu', 'Invasive', 'Normal')
prefixes = {'Benign': 'b', 'InSitu': 'is', 'Invasive': 'iv', 'Normal': 'n'}

###

for c in classes:
    for i in range(100):
        filename = prefixes[c] + mu.i2str(i + 1) + '.tif'
        print('Doing Image {}'.format(filename))
        path = os.path.join(data_dir, c, filename)
        image = mu.read_image(path)

        save_filename = prefixes[c] + mu.i2str(i + 1) + '_thumb.png'
        save_path = os.path.join(save_dir, c, save_filename)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        mu.save_aspng(image, save_path, compression=5)
