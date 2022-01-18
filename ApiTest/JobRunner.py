import datetime
import threading
import copy
from django.db.models import Count, Max
from ApiTest.ApiKeywords import ApiKeywords
from ApiTest.VarMap import VarMap
from ApiTest.models import ApiCase, ApiCaseStep, ApiTestBatch, ApiCaseResult, ApiStepResult, ApiGroupEnv
from ApiTest.models import ApiCaseParam, ApiCaseParamValues


def set_scene_param(param_dict, index, case_var_map):
    """
       添加场景环境变量
    :param param_dict: 用例环境变量字典
    :param index: 当前场景序号
    :param case_var_map: 公共环境变量
    :return: 场景环境变量字典,包括用例组公共环境变量和当前场景环境变量
    """
    v_map = copy.deepcopy(case_var_map)
    for p_name in param_dict.keys():
        if len(param_dict[p_name]) < 1:
            continue
        if index > len(param_dict[p_name]) - 1:
            v_map.set_var(p_name, param_dict[p_name][-1])
        else:
            v_map.set_var(p_name, param_dict[p_name][index])
    return v_map


class RunnerThread(threading.Thread):
    """
        多线程执行
    """

    def __init__(self, cases, batch, debug=False, stop_after_fail=False):
        threading.Thread.__init__(self)
        self.cases = cases
        self.batch = batch
        self.debug = debug
        self.stop_after_fail = stop_after_fail

    def run(self):
        batch_result = True
        for case in self.cases:
            if 'id' not in case.keys():
                continue
            case_result = True
            case_var_map = VarMap()
            # 添加用例组环境变量
            env = ApiGroupEnv.objects.filter(group__apicase__id=case['id'])
            if env:
                case_var_map = set_group_env(case_var_map, env)
            # api = ApiKeywords(case_var_map, debug=self.debug)
            api_case = ApiCase.objects.filter(id=case['id'])
            steps = ApiCaseStep.objects.filter(case=api_case[0]).order_by('step_order')
            if not steps or not case:
                continue
            params = ApiCaseParam.objects.filter(case__id=case['id']).values('id', 'p_name').annotate(
                count=Count('apicaseparamvalues__p_value'))
            if params:
                max_count = params.aggregate(max_count=Max('count'))['max_count']
                param_dict = {}
                for param in params:
                    param_dict[param['p_name']] = list(
                        ApiCaseParamValues.objects.filter(param=param['id']).values_list('p_value', flat=True))
                for index in range(max_count):
                    # 当前场景环境变量
                    scene_var_map = set_scene_param(param_dict, index, case_var_map)
                    api = ApiKeywords(scene_var_map, debug=self.debug)
                    case_title = api_case[0].title + f'_#{index + 1}' if max_count > 1 else api_case[0].title
                    case_result = self.execute_case(api_case[0], case_title, api, steps, case_result)
            else:
                api = ApiKeywords(case_var_map, debug=self.debug)
                case_result = self.execute_case(api_case[0], api_case[0].title, api, steps, case_result)
            # case_res = ApiCaseResult(batch=self.batch, case=api_case[0], case_title=api_case[0].title,
            #                          create_time=datetime.datetime.now(), result='9')
            # case_res.save()
            # case_result = self.execute_steps(steps, case_result, api, case_res, stop_after_fail=self.stop_after_fail)
            # case_res.result = '0' if case_result else '1'
            # case_res.save()
            batch_result = batch_result and case_result
        self.batch.result = '0' if batch_result else '1'
        self.batch.save()

    def execute_case(self, api_case_obj, api_case_title, api, steps, case_result):
        case_res = ApiCaseResult(batch=self.batch, case=api_case_obj, case_title=api_case_title,
                                 create_time=datetime.datetime.now(), result='9')
        case_res.save()
        case_result = self.execute_steps(steps, case_result, api, case_res, stop_after_fail=self.stop_after_fail)
        case_res.result = '0' if case_result else '1'
        case_res.save()
        return case_result

    def execute_steps(self, steps, case_result, api, case_res, stop_after_fail=False):
        for step in steps:
            step_res = ApiStepResult(batch=self.batch, case=case_res, step=step, step_title=step.title,
                                     step_action=step.step_action, result='9')
            if not str(step.step_action).isdigit() and hasattr(api, step.step_action):
                try:
                    func = getattr(api, step.step_action)
                    res, info = func(*(step.step_p1, step.step_p2))
                    case_result = case_result and res
                    result = '0' if res else '1'
                    step_res.result = result
                    step_res.info = info.replace('<', '{').replace('>', '}')[:2047]
                    # ApiStepResult(batch=self.batch, case=case_res, step=step, step_title=step.title, result=result,
                    #               info=info[:2047], create_time=datetime.datetime.now()).save()
                except Exception as e:
                    error = e.__str__()[:2047] if len(e.__str__()) > 2048 else e.__str__()
                    case_result = False
                    step_res.result = '1'
                    step_res.info = error
                    # ApiStepResult(batch=self.batch, case=case_res, step=step, step_title=step.title, result='1',
                    #               info=error, create_time=datetime.datetime.now()).save()
            elif str(step.step_action).isdigit():
                case = ApiCase.objects.filter(id=step.step_action)
                child_case_steps = ApiCaseStep.objects.filter(case_id=case[0].id).order_by('step_order')
                if child_case_steps:
                    # 增加用例调用起始记录
                    ApiStepResult(batch=self.batch, case=case_res, step=step, step_title=step.title,
                                  step_action=step.title, result='0', info=f'Start call case: {case[0].title}.',
                                  create_time=datetime.datetime.now()).save()
                    child_case_result = self.execute_steps(child_case_steps, case_result, api, case_res)
                    case_result = case_result and child_case_result
                    # 调用用例,action改为用例title
                    step_res.step_action = step.title
                    step_res.result = '0' if child_case_result else '1'
                    step_res.info = f'End of case call: {case[0].title}.'
            else:
                case_result = False
                step_res.result = '1'
                step_res.info = 'No such keyword.'
                # ApiStepResult(batch=self.batch, case=case_res, step=step, step_title=step.title, result='1',
                #               info='No such keyword.', create_time=datetime.datetime.now()).save()
            step_res.create_time = datetime.datetime.now()
            step_res.save()
            if stop_after_fail and step_res.result != '0':
                break
        return case_result


def api_job_run(cases, tester, debug=False, stop_after_fail=False):
    batch = ApiTestBatch(tester=tester, create_time=datetime.datetime.now(), result='9')
    batch.save()
    thd = RunnerThread(cases, batch, debug=debug, stop_after_fail=stop_after_fail)
    thd.start()


def set_group_env(varmap: VarMap, group_env):
    if group_env:
        for row in group_env:
            if row.env_key and row.env_value:
                varmap.set_var(row.env_key, row.env_value)
            else:
                continue
    return varmap
