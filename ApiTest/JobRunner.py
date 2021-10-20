import datetime
import threading
from ApiTest.ApiKeywords import ApiKeywords
from ApiTest.VarMap import VarMap
from ApiTest.models import ApiCase, ApiCaseStep, ApiTestBatch, ApiCaseResult, ApiStepResult, ApiGroupEnv


class RunnerThread(threading.Thread):
    """
        多线程执行
    """

    def __init__(self, cases, batch, debug=False):
        threading.Thread.__init__(self)
        self.cases = cases
        self.batch = batch
        self.debug = debug

    def run(self):
        batch_result = True
        for case in self.cases:
            case_result = True
            case_var_map = VarMap()
            env = ApiGroupEnv.objects.filter(group__apicase__id=case['id'])
            if env:
                case_var_map = set_group_env(case_var_map, env)
            api = ApiKeywords(case_var_map, debug=self.debug)
            if 'id' not in case.keys():
                continue
            api_case = ApiCase.objects.filter(id=case['id'])
            steps = ApiCaseStep.objects.filter(case__id=api_case[0].id).order_by('step_order')
            if not steps or not case:
                continue
            case_res = ApiCaseResult(batch=self.batch, case=api_case[0], create_time=datetime.datetime.now(), result='9')
            case_res.save()
            case_result = self.execute_steps(steps, case_result, api, case_res)
            # for step in steps:
            #     if hasattr(api, step.step_action):
            #         try:
            #             func = getattr(api, step.step_action)
            #             res, info = func(*(step.step_p1, step.step_p2))
            #             case_result = case_result and res
            #             result = '0' if res else '1'
            #             ApiStepResult(batch=self.batch, case=case_res, step=step, result=result, info=info,
            #                           create_time=datetime.datetime.now()).save()
            #         except Exception as e:
            #             error = e.__str__()[:2047] if len(e.__str__()) > 2048 else e.__str__()
            #             case_result = False
            #             ApiStepResult(batch=self.batch, case=case_res, step=step, result='1',
            #                           info=error, create_time=datetime.datetime.now()).save()
            #     else:
            #         case_result = False
            #         ApiStepResult(batch=self.batch, case=case_res, step=step, result='1', info='No such keyword.',
            #                       create_time=datetime.datetime.now()).save()
            case_res.result = '0' if case_result else '1'
            case_res.save()
            batch_result = batch_result and case_result
        self.batch.result = '0' if batch_result else '1'
        self.batch.save()

    def execute_steps(self, steps, case_result, api, case_res):
        for step in steps:
            if not str(step.step_action).isdigit() and hasattr(api, step.step_action):
                try:
                    func = getattr(api, step.step_action)
                    res, info = func(*(step.step_p1, step.step_p2))
                    case_result = case_result and res
                    result = '0' if res else '1'
                    ApiStepResult(batch=self.batch, case=case_res, step=step, result=result, info=info[:2047],
                                  create_time=datetime.datetime.now()).save()
                except Exception as e:
                    error = e.__str__()[:2047] if len(e.__str__()) > 2048 else e.__str__()
                    case_result = False
                    ApiStepResult(batch=self.batch, case=case_res, step=step, result='1',
                                  info=error, create_time=datetime.datetime.now()).save()
            elif str(step.step_action).isdigit():
                case = ApiCase.objects.filter(id=step.step_action)
                child_case_steps = ApiCaseStep.objects.filter(case_id=case[0].id)
                if child_case_steps:
                    case_result = case_result and self.execute_steps(child_case_steps, case_result, api, case_res)
            else:
                case_result = False
                ApiStepResult(batch=self.batch, case=case_res, step=step, result='1', info='No such keyword.',
                              create_time=datetime.datetime.now()).save()
        return case_result


def api_job_run(cases, tester, debug=False):
    batch = ApiTestBatch(tester=tester, create_time=datetime.datetime.now(), result='9')
    batch.save()
    thd = RunnerThread(cases, batch, debug=debug)
    thd.start()


def set_group_env(varmap: VarMap, group_env):
    if group_env:
        for row in group_env:
            if row.env_key and row.env_value:
                varmap.set_var(row.env_key, row.env_value)
            else:
                continue
    return varmap



