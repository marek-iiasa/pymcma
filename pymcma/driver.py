import sys		# needed for sys.exit()
import pyomo.environ as pe
from pyomo.opt import SolverStatus
from pyomo.opt import TerminationCondition
from .ctr_mca import CtrMca  # handling MCMA structure and data, uses Crit class
from .rd_inst import rd_inst  # model instance provider
from .mc_block import McMod  # generate the AF sub-model/block and link the core-model variables with AF variables
from .par_repr import ParRep
from .report import Report  # organize results of each iteration into reports


# noinspection SpellCheckingInspection
def chk_sol(res):  # check status of the solution
    # print(f'solver status: {res.solver.status}, termination condition: {res.solver.termination_condition}.')
    if ((res.solver.status != SolverStatus.ok) or
            (res.solver.termination_condition != TerminationCondition.optimal)):
        print(f'optimization failed; termination condition: {res.solver.termination_condition}')
        sys.stdout.flush()  # desired for assuring printing exception at the output end
        '''
        # non-optimal solutions are handled now, commented exceptions kept here in case they should be needed
        if res.solver.termination_condition == TerminationCondition.infeasible:
            raise Exception('Optimization problem is infeasible.')
        elif res.solver.termination_condition == TerminationCondition.unbounded:
            raise Exception('Optimization problem is unbounded.')
        else:
            raise Exception('Optimization failed.')
        '''
        return False     # optimization failed
    else:
        return True     # optimization OK


# noinspection SpellCheckingInspection
def driver(cfg):
    m1 = rd_inst(cfg)    # upload or generate m1 (core model)
    print(f'Generating Pareto-front representation of the core-model instance: {m1.name}.')

    # is_par_rep = True/False: can be specified in cfg_usr.yml
    mc = CtrMca(cfg)    # CtrMca ctor

    # list of the core-model variables, values of which shall be included in the report can be specified in cfg_usr.yml
    rep = Report(cfg, mc, m1)    # Report ctor

    # select solver
    opt = pe.SolverFactory('glpk')
    # opt = pe.SolverFactory('ipopt') # solves both LP and NLP

    n_iter = 0
    max_itr = cfg.get('mxIter')
    print(f'Maximum number of iterations: {max_itr}')
    while n_iter < max_itr:   # just for safety; should not be needed for a proper stop criterion
        i_stage = mc.set_stage()  # define/check current analysis stage
        print(f'\nStart iteration {n_iter}, analysis stage {i_stage} -----------------------------------------------')

        m = pe.ConcreteModel()  # model instance to be composed of two blocks: (1) core model and (2) mc_part
        m.add_component('core_model', m1)  # m.m1 = m1  assign works but (due to warning) replaced by add_component()

        if i_stage > 3 and mc.is_par_rep and mc.par_rep is None:    # init ParRep() (must be after payOff table done)
            mc.par_rep = ParRep(mc)

        # the MC-part model-block (based on preferences: either generated by the MCMA or uploaded)
        if i_stage < 4:
            print('Setting preferences for next step in Payoff table computations.')
        elif i_stage == 4:
            print('Setting preferences for computing initial and (optional) neutral solution.')
        else:   # i_stage == 5
            if mc.is_par_rep:
                print('Generate preferences for exploration of the Pareto set representation.')
            else:
                print('Use preferences provided in a file.')
        mc.set_pref()  # set preferences (crit activity, optionally A/R values)
        if mc.cur_stage == 6:   # cur_stage is set to 6 (by par_pref() or set_pref()), if all preferences are processed
            print(f'\nFinished the analysis for all specified preferences.')
            break       # exit the iteration loop
        # print(f'\nGenerating instance of the MC-part model (representing the MCMA Achievement Function).')
        mc_gen = McMod(mc, m1)      # McMod ctor (model representing the MC-part, i.e. the Achievement Function of MCMA)
        mc_part = mc_gen.mc_itr()   # concrete model of the MC-part (based on the current preferences)
        if mc_part is None:
            print(f'\nThe defined preferences cannot be used for defining the mc-block')
            print('Optimization problem not generated.     ---------------------------------------------------------')
            mc.is_opt = False
        else:
            # print('mc-part generated.\n')
            # mc_part.pprint()
            m.add_component('mc_part', mc_part)  # add_component() used instead of simple assignment
            if mc.verb > 3:
                print('core-model and mc-part blocks added to the model instance; ready for optimization.')
                m.pprint()

            # solve the model instance composed of two blocks: (1) core model m1, (2) MC-part (Achievement Function)
            # print('\nsolving --------------------------------')
            # results = opt.solve(m, tee=True)
            results = opt.solve(m, tee=False)
            # m1.load(results)  # Loading solution into results object
            mc.is_opt = chk_sol(results)  # solution status: True, if optimal, False otherwise
            if mc.is_opt:  # optimal solution found
                # print(f'\nOptimal solution found.')
                pass
            else:   # optimization failed
                print(f'\nOptimization failed, solution disregarded.         ----------------------------------------')
        # print('processing solution ----')
        rep.itr(mc_part)  # driver for sol-processing: update crit. attr., store sol, check domination & close sols
        m.del_component(m.core_model)  # must be deleted (otherwise m1 would have to be generated at every iteration)
        # m.del_component(m.mc_part)   # need not be deleted (a new mc_part needs to be generated for new preferences)

        # print(f'Finished current itr, count: {n_iter}.')
        n_iter += 1
        if n_iter > max_itr:
            print(f'\nMax iters {max_itr} reached; breaking the iteration loop.\n')
            break
    # the iteration loop ends here

    print(f'\nFinished {n_iter} analysis iterations. Summary report follows.')

    # reports
    rep.summary()   # generate data-frames and store them as csv
