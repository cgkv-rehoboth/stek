import csv
import datetime
import tempfile

import pandas as panda
from dateutil import parser

from base.views import get_delimiter


class DataValidationError(Exception):
  def __init__(self, message):
    self.message = message
  pass


class HeaderValidationError(DataValidationError):
  def __init__(self, message, missing_headers):
    self.message = message
    self.missing_headers = missing_headers


def excel_to_lines(file, headers):
  df = panda.read_excel(file,
                        usecols=(len(headers) - 1),   # Parse only necessary columns
                        nrows=1000,                    # Overload safety
                        # dtype=str,
                        )

  # Check file headers
  missingheaders = list(set(headers) - set(df.columns))
  if missingheaders:
    raise HeaderValidationError('Headers are not equal!', missingheaders)

  if len(df.index) < 1:
    raise DataValidationError('No data!')

  lines = []
  for i, row in df.iterrows():
    line = {}
    for header in headers:
      value = row[header]

      if panda.isna(value):                     # Convert empty types
        value = ''
      elif isinstance(value, datetime.time):    # Convert time types
        value = value.strftime("%H:%M")
      elif isinstance(value, panda.Timestamp):  # Convert datetime types
        value = value.strftime("%d-%m-%Y")
      elif isinstance(value, datetime.datetime):  # Convert datetime types
        value = value.strftime("%d-%m-%Y")
      elif header == 'Datum':                   # Convert string datetime types
        datetime_obj = parser.parse(value)
        value = datetime_obj.strftime("%d-%m-%Y")

      line[header] = value
    lines.append(line)

  return lines


def csv_to_lines(file, headers):
  # Create a temp file
  with tempfile.NamedTemporaryFile() as tf:
    # Copy the uploaded file to the temp file
    for chunk in file.chunks():
      tf.write(chunk)

    # Save contents to file on disk
    tf.flush()

    # Read file
    with open(tf.name, 'r', encoding="ISO-8859-1") as fh:
      csv_lines = csv.DictReader(fh, delimiter=get_delimiter(fh))

      # Check for needed headers
      missingheaders = list(set(headers) - set(csv_lines.fieldnames))
      if missingheaders:
        print(headers)
        print(csv_lines.fieldnames)
        print(missingheaders)
        raise HeaderValidationError('Headers are not equal!', missingheaders)

      # Get lines
      lines = [line for line in csv_lines]

      if len(lines) < 1:
        raise DataValidationError('No data!')

  return lines
