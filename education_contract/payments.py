# -*- coding: iso-8859-1 -*-

from openerp import models, fields, api
from datetime import datetime, timedelta
from dateutil import parser
from openerp.exceptions import ValidationError
from openerp.exceptions import except_orm, Warning, RedirectWarning


