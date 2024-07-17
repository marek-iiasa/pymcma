import sys		# needed for sys.exit()
import pyomo.environ as pe
from pyomo.opt import SolverStatus
from pyomo.opt import TerminationCondition
# from .ctr_mca import CtrMca  # handling MCMA structure and data, uses Crit class
from .rd_inst import rd_inst  # model instance provider
from .wrkflow import WrkFlow  # app's workflow
from .mc_block import McMod  # generate the AF sub-model/block and link the core-model variables with AF variables
# from .par_repr import ParRep
# from .report import Report  # organize results of each iteration into reports


# noinspection SpellCheckingInspection
def chk_sol(res):  # check status of the solution
    # print(f'solver status: {res.solver.status}, termination condition: {res.solver.termination_condition}.')
    if ((res.solver.status != SolverStatus.ok) or
            (res.solver.termination_condition != TerminationCondition.optimal)):
        print(f'optimization failed; termination condition: {res.solver.termination_condition}')
        sys.stdout.flush()  # desired for assuring printing exception at the output end
        return False     # optimization failed
    else:
        return True     # optimization OK


# noinspection SpellCheckingInspection
def driver(cfg):
    m1 = rd_inst(cfg)    # upload or generate m1 (core model)
    print(f'Generating Pareto-front representation of the core-model instance: {m1.name}.')

    # initialize the WrkFlow
    wflow = WrkFlow(cfg, m1)
    verb = wflow.mc.verb

    # select solver (default glpk, other solvers can be selected in cfg.yml by: solver: solver_id
    # glpk - solves LP and MIP; iopt - solves LP and NL, but not MIP; gams uses cplex (but with the interface overhead)
    solver_id = wflow.mc.opt('solver', 'glpk')
    print(f'Selected solver_id: {solver_id}')
    opt = pe.SolverFactory(solver_id)

    n_iter = 0
    max_itr = wflow.mc.opt('mxIter', 100)
    print(f'Maximum number of iterations: {max_itr}')
    while n_iter < max_itr:   # just for safety; should not be needed for a proper stop criterion
        # i_stage = mc.set_stage()  # define/check current analysis stage
        print(f'\nStart iteration {n_iter}, analysis stage {wflow.cur_stage} -----------------------------------------')
        i_stage = wflow.itr_start(n_iter)   # set preferences, return current stage

        m = pe.ConcreteModel()  # model instance to be composed of two blocks: (1) core model and (2) mc_part
        m.add_component('core_model', m1)  # m.m1 = m1  assign works but (due to warning) replaced by add_component()
        mc_gen = McMod(wflow, m1)  # McMod ctor (the MC-part model, i.e. the Achievement Function of MCMA)
        mc_part = mc_gen.mc_itr()   # concrete model of the MC-part (based on the current preferences)
        if mc_part is None:
            print(f'\nThe defined preferences cannot be used for defining the mc-block')
            print('Optimization problem not generated.     ---------------------------------------------------------')
            wflow.mc.is_opt = False
        else:
            # print('mc-part generated.\n')
            # mc_part.pprint()
            m.add_component('mc_part', mc_part)  # add_component() used instead of simple assignment
            if verb > 3:
                print('core-model and mc-part blocks added to the model instance; ready for optimization.')
                m.pprint()

            # solve the model instance composed of two blocks: (1) core model m1, (2) MC-part (Achievement Function)
            # print('\nsolving --------------------------------')
            # results = opt.solve(m, tee=True)
            results = opt.solve(m, tee=False)
            wflow.mc.is_opt = chk_sol(results)  # solution status: True, if optimal, False otherwise

        # print('processing solution ----')
        if wflow.mc.is_opt:
            i_stage = wflow.itr_sol(mc_part)  # process solution, set next stage in wflow, and return it
        else:
            print(f'\niter {n_iter}: optimization failed, solution disregarded.        -------------------------------')
        # rep.itr(mc_part)  # driver for sol-processing: update crit. attr., store sol, check domination & close sols
        m.del_component(m.core_model)  # must be deleted (otherwise m1 would have to be generated at every iteration)
        # m.del_component(m.mc_part)   # need not be deleted (a new mc_part needs to be generated for new preferences)

        # print(f'Finished current itr, count: {n_iter}.')
        if i_stage == 6:   # cur_stage is set to 6 (by par_pref() or set_pref()), if all preferences are processed
            print(f'\nFinished the analysis for all generated/specified preferences.')
            break       # exit the iteration loop
        n_iter += 1
        if n_iter > max_itr:
            print(f'\nMax iters {max_itr} reached; breaking the iteration loop.\n')
            break
    # the iteration loop ends here

    print(f'\nFinished {n_iter} analysis iterations. Summary report follows.')

    # reports
    wflow.rep.summary()   # generate data-frames and store them as csv
