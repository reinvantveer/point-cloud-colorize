# -*- coding: utf-8 -*-
"""
Python3

@author: Chris Lucas
"""

import argparse
import json
from pathlib import Path

import pdal


PDAL_PIPELINE = """{{
  "pipeline":[
    {{
      "type": "readers.las",
      "filename": "{input_file}"
    }},
    {{
      "type": "filters.python",
      "script": "{directory}/pdal_colorize.py",
      "function": "las_colorize",
      "module": "anything",
      "pdalargs": "{pdalargs}"
    }},
    {{
      "type": "writers.las",
      "a_srs": "{srs}",
      "filename": "{output_file}"
    }}
  ]
}}"""


def run_pdal(input_path, output_path, las_srs, wms_url,
             wms_layer, wms_srs, wms_version, wms_format,
             wms_pixel_size, wms_max_image_size):
    """
    Run the pdal pipeline using the given arguments.

    Parameters
    ----------
    input_path : str
        The path to the input LAS/LAZ file or directory containing LAS/LAZ
        files.
    output_path : str
        The path to the output LAS/LAZ file or directory.
    las_srs : str
        The spatial reference system of the LAS data.
    wms_url : str
        The url of the WMS service to use.
    wms_layer : str
        The layer of the WMS service to use.
    wms_srs : str
        The spatial reference system of the WMS data to request.
    wms_version : str
        The image format of the WMS data to request.
    wms_format : str
        The version number of the WMS service.
    wms_pixel_size : float
        The approximate desired pixel size of the requested image.
    wms_max_image_size : int
        The maximum size (in pixels) of the largest side of the requested
        image.
    """
    pdalargs = {'wms_url': wms_url,
                'wms_layer': wms_layer,
                'wms_srs': wms_srs,
                'wms_version': wms_version,
                'wms_format': wms_format,
                'wms_pixel_size': wms_pixel_size,
                'wms_max_image_size': wms_max_image_size,
                'las_srs': las_srs}
    pdalargs_str = json.dumps(pdalargs).replace('"', '\\"')

    path = Path(__file__)
    pipeline_json = PDAL_PIPELINE.format(input_file=input_path.as_posix(),
                                         output_file=output_path.as_posix(),
                                         srs=las_srs,
                                         pdalargs=pdalargs_str,
                                         directory=path.parent.as_posix())
    pipeline = pdal.Pipeline(pipeline_json)
    pipeline.validate()
    pipeline.execute()


def process_files(input_path, output_path, las_srs,
                  wms_url, wms_layer, wms_srs,
                  wms_version, wms_format, wms_pixel_size,
                  wms_max_image_size, verbose=False):
    """
    Run the pdal pipeline for the input files.

    Parameters
    ----------
    input_path : str
        The path to the input LAS/LAZ file or directory containing LAS/LAZ
        files.
    output_path : str
        The path to the output LAS/LAZ file or directory.
    las_srs : str
        The spatial reference system of the LAS data.
    wms_url : str
        The url of the WMS service to use.
    wms_layer : str
        The layer of the WMS service to use.
    wms_srs : str
        The spatial reference system of the WMS data to request.
    wms_version : str
        The image format of the WMS data to request.
    wms_format : str
        The version number of the WMS service.
    wms_pixel_size : float
        The approximate desired pixel size of the requested image.
    wms_max_image_size : int
        The maximum size (in pixels) of the largest side of the requested
        image.
    verbose : bool
        Set verbose.
    """
    input_path = Path(input_path)
    output_path = Path(output_path)

    if input_path.is_dir():
        for f in input_path.iterdir():
            if f.suffix == '.las' or f.suffix == '.laz':

                if output_path.is_dir():
                    out = output_path / '{}_color{}'.format(f.stem, f.suffix)
                else:
                    raise ValueError('Output path should be a directory if '
                                     'the input path is a directory.')

                if verbose:
                    print('Colorizing {} ..'.format(f))
                    print('Saving at {}.'.format(out))

                run_pdal(f, out, las_srs, wms_url, wms_layer, wms_srs,
                         wms_version, wms_format, wms_pixel_size,
                         wms_max_image_size)
    else:
        if verbose:
            print('Colorizing {} ..'.format(input_path))

        if output_path.suffix == '.las' or output_path.suffix == '.laz':
            if verbose:
                print('Saving at {}.'.format(output_path))

            run_pdal(input_path, output_path, las_srs, wms_url,
                     wms_layer, wms_srs, wms_version, wms_format,
                     wms_pixel_size, wms_max_image_size)
        elif output_path.is_dir():
            out = output_path / '{}_color{}'.format(input_path.stem,
                                                    input_path.suffix)

            if verbose:
                print('Saving at {}.'.format(out))

            run_pdal(input_path, out, las_srs, wms_url,
                     wms_layer, wms_srs, wms_version, wms_format,
                     wms_pixel_size, wms_max_image_size)
        else:
            raise ValueError('Specified output path not a LAS/LAZ file or '
                             'existing directory.')


def argument_parser():
    """
    Define and return the arguments.
    """
    description = ('Colorize a las or laz file with a WMS service. '
                   'By default uses PDOK aerial photography.')
    parser = argparse.ArgumentParser(description=description)
    required_named = parser.add_argument_group('required named arguments')
    required_named.add_argument('-i', '--input',
                                help='The input LAS/LAZ file or folder.',
                                required=True)
    required_named.add_argument('-o', '--output',
                                help=('The output colorized LAS/LAZ '
                                      'file or folder.'),
                                required=True)
    parser.add_argument('-s', '--las_srs',
                        help=('The spatial reference system of the LAS data. '
                              '(str, default: EPSG:28992)'),
                        required=False,
                        default='EPSG:28992')
    parser.add_argument('-w', '--wms_url',
                        help=('The url of the WMS service to use. '
                              '(str, default: https://geodata. '
                              'nationaalgeoregister.nl/luchtfoto/rgb/wms?)'),
                        required=False,
                        default=('https://geodata.nationaalgeoregister.nl'
                                 '/luchtfoto/rgb/wms?'))
    parser.add_argument('-l', '--wms_layer',
                        help=('The layer of the WMS service to use. '
                              '(str, default: Actueel_ortho25)'),
                        required=False,
                        default='Actueel_ortho25')
    parser.add_argument('-r', '--wms_srs',
                        help=('The spatial reference system of the WMS data '
                              'to request. (str, default: EPSG:28992)'),
                        required=False,
                        default='EPSG:28992')
    parser.add_argument('-f', '--wms_format',
                        help=('The image format of the WMS data to request. '
                              '(str, default: image/png)'),
                        required=False,
                        default='image/png')
    parser.add_argument('-v', '--wms_version',
                        help=('The version number of the WMS service. '
                              '(str, default: 1.3.0)'),
                        required=False,
                        default='1.3.0')
    parser.add_argument('-p', '--wms_pixel_size',
                        help=('The approximate desired pixel size of the '
                              'requested image. (float, default: 0.25)'),
                        required=False,
                        default=0.25)
    parser.add_argument('-m', '--wms_max_image_size',
                        help=('The maximum size (in pixels) of the largest '
                              'side of the requested image. '
                              '(int, default: 1000)'),
                        required=False,
                        default=1000)
    parser.add_argument('-V', '--verbose', default=False, action="store_true",
                        help='Set verbose.')
    args = parser.parse_args()
    return args


def main():
    """
    Run the application.
    """
    args = argument_parser()
    process_files(args.input, args.output, args.las_srs,
                  args.wms_url, args.wms_layer, args.wms_srs,
                  args.wms_version, args.wms_format,
                  args.wms_pixel_size, args.wms_max_image_size,
                  args.verbose)


if __name__ == '__main__':
    main()
