import datetime
import threading
from ApiTest.ApiKeywords import ApiKeywords
from ApiTest.VarMap import VarMap
from ApiTest.models import ApiCase, ApiCaseStep, ApiTestBatch, ApiCaseResult, ApiStepResult


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
            api = ApiKeywords(case_var_map, debug=self.debug)
            if 'id' not in case.keys():
                continue
            api_case = ApiCase.objects.filter(id=case['id'])
            steps = ApiCaseStep.objects.filter(case__id=api_case[0].id).order_by('step_order')
            if not steps or not case:
                continue
            case_res = ApiCaseResult(batch=self.batch, case=api_case[0], create_time=datetime.datetime.now())
            case_res.save()
            for step in steps:
                if hasattr(api, step.step_action):
                    try:
                        func = getattr(api, step.step_action)
                        res, info = func(*(step.step_p1, step.step_p2))
                        case_result = case_result and res
                        result = '0' if res else '1'
                        ApiStepResult(batch=self.batch, case=case_res, step=step, result=result, info=info,
                                      create_time=datetime.datetime.now()).save()
                    except Exception as e:
                        error = e.__str__()[:2047] if len(e.__str__()) > 2048 else e.__str__()
                        case_result = False
                        ApiStepResult(batch=self.batch, case=case_res, step=step, result='1',
                                      info=error, create_time=datetime.datetime.now()).save()
                else:
                    case_result = False
                    ApiStepResult(batch=self.batch, case=case_res, step=step, result='1', info='No such keyword.',
                                  create_time=datetime.datetime.now()).save()
            case_res.result = '0' if case_result else '1'
            case_res.save()
            batch_result = batch_result and case_result
        self.batch.result = '0' if batch_result else '1'
        self.batch.save()


def api_job_run(cases, tester, debug=False):
    batch = ApiTestBatch(tester=tester, create_time=datetime.datetime.now())
    batch.save()
    thd = RunnerThread(cases, batch, debug=debug)
    thd.start()
