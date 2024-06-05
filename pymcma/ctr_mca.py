"""
Handle data structure and control flows of the MCMA
"""
# import sys      # needed from stdout
# import os
import math
# from os import R_OK, access
# from os.path import isfile
from .crit import Crit      # , CrPref
# from .par_repr import ParRep


# noinspection SpellCheckingInspection
class CtrMca:   # control flows of MCMA at diverse computations states
    def __init__(self, wflow):   # par_rep False/True controls no/yes Pareto representation mode
        self.wflow = wflow
        self.cfg = wflow.cfg
        self.f_crit = 'config.txt'   # file with criteria specification
        self.cr = []        # objects of Crit class, each representing the corresponding criterion
        self.n_crit = 0     # number of defined criteria == len(self.cr)
        self.deg_exp = False    # expansion of degenerated cube dimensions
        # tolerances
        self.cafAsp = 100.   # value of CAF at A (if A undefined, then at U)
        self.critScale = 1000.   # range [utopia, nadir] of scaled values (used in self.scale())
        self.epsilon = 1.e-6  # fraction of self.cafAsp used for scaling the AF regularizing term
        #
        self.minDiff = 0.001  # min. relative differences between (U, N), (U, A), (A, R), (R, N) (was 0.01)
        self.slopeR = 10.    # slope ratio between mid-segment and segments above A and below R
        # diverse
        # self.scVar = self.opt('scVar', True)   # scale core-model vars defining CAFs
        self.scVar = self.opt('scVar', False)   # scale core-model vars defining CAFs
        self.verb = self.opt('verb', 1)   # print verbosity: 0 - min., 1 - key, 2 - debug, 3 - detailed
        # the below to be used for user-defined preferences (currently not used)
        # self.f_pref = 'pref.txt'     # file with defined preferences' set, currently not used
        # self.pref = []    # list of preferences defined for each blocks
        # self.n_pref = 0     # number of blocks of read-in preferences
        self.cur_pref = 0   # index of currently processed preference

        self.epsilon = self.opt('eps', self.epsilon)  # scaling of the AF regularizing term
        print(f'epsilon = {self.epsilon:.1e}')
        do_neutral = self.opt('neutral', True) is True
        print(f'generate neutral solution = {do_neutral}')
        #
        self.rdCritSpc()    # read criteria specs from the config file

    def opt(self, key_id, def_val):     # return: the cfg value if specified; otherwise the default
        val = self.cfg.get(key_id)
        if val is None:
            return def_val
        else:
            return val

    def rdCritSpc(self):    # read specification of criteria
        print(f'\nCreating criteria defined in cfg_usr.yml file.')
        cr_def = self.cfg.get('crit_def')
        assert cr_def is not None, f'Criteria not defined in the cfg_usr.yml file.'
        self.n_crit = len(cr_def)
        for i, cr in enumerate(cr_def):
            n_words = len(cr)  # crit-name, type (min or max), name of core-model var defining the crit.
            assert n_words == 3, f'definition of {i}-th criterion has {n_words} elements instead of the required three.'
            self.addCrit(cr[0], cr[1], cr[2])  # store the criterion specs
        assert (self.n_crit > 1), f'at least two criteria need to be defined, only {self.n_crit} was defined.'

    def addCrit(self, cr_name, typ, var_name):
        """
        Add definition of a criterion.

        :param cr_name: criterion name
        :type cr_name:  str
        :param var_name: name of the corresponding model variable
        :type var_name:  str
        :param typ: criterion type (either 'min' or 'max')
        :type typ:  str
        :return:  None
        """
        if self.cr_ind(cr_name, False) == -1:  # add, if the cr_name is not already used
            self.cr.append(Crit(cr_name, var_name, typ))
            self.n_crit = len(self.cr)
        else:
            raise Exception(f'addCrit(): duplicated criterion name: "{cr_name}".')

    def cr_ind(self, cr_name, fatal=True):  # return index (in self.cr) of criterion having name cr_name
        for (i, crit) in enumerate(self.cr):
            if crit.name == cr_name:
                return i
        if fatal:   # raise exception
            raise Exception(f'cr_ind(): unknown criterion name: "{cr_name}".')
        else:   # only inform
            return -1

    def scale(self):    # define scaling-coeffs (for scaling criteria values to the same range of values)
        print(f'\nDefining criteria scaling coefficients.')
        for cr in self.cr:
            diff = abs(cr.utopia - cr.nadir)
            assert diff > self.minDiff, f'Crit. "{cr.name}" utopia {cr.utopia:.4e} too close to nadir {cr.nadir}:.4e.'
            sc_tmp = self.critScale / diff
            magn = int(math.log10(sc_tmp))
            cr.sc_var = math.pow(10, magn)
            print(f'Criterion "{cr.name}", {cr.attr}: scaling coef. = {cr.sc_var:.1e}, utopia {cr.utopia:.2e}, ' 
                  f'nadir {cr.nadir:.2e}\n\tnot-rounded scaling (to range {self.critScale:.1e}) = {sc_tmp:.4e}.')

    # store crit values from last solution, called from Report::itr(), after check that sol is in the U/N range
    def critVal(self, crit_val):
        for cr in self.cr:
            val = crit_val.get(cr.name)
            cr.val = val
            if self.wflow.cur_stage > 1:
                cr.a_val = cr.val2ach(cr.val)
                if self.verb > 2:
                    print(f'\tCrit {cr.name}: val {cr.val:.2f}, a_val {cr.a_val:.2f}')

    def diffOK(self, i, val1, val2):  # return True if the difference of two values of i-th is large enough
        maxVal = max(abs(self.cr[i].utopia), (abs(self.cr[i].nadir)))  # value used as basis for min-differences
        minDiff = self.minDiff * maxVal
        if abs(val1 - val2) >= minDiff:
            return True
        else:
            return False

