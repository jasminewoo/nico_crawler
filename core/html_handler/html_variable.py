class HTMLVariable:
    def __init__(self, tag_conditions, data_key=None):
        if not tag_conditions or type(tag_conditions) is not list or len(tag_conditions) == 0:
            msg = "'tag_conditions' must be a list of dictionaries; containing at least 1 element"
            raise AssertionError(msg)

        self.data = None
        self._data_buffer = ''
        self.data_key = data_key
        self.tag_conditions = tag_conditions
        self.tag_condition_satisfaction = [False] * len(tag_conditions)
        self.end_tag = determine_end_tag(tag_conditions)

    def process_start_tag(self, tag, attrs):
        if self.data:
            return

        if self.is_detected:
            self.process_data(to_string(tag, attrs))
            return

        tag_specs = dict(map(lambda x: ('{}.{}'.format(tag, x), attrs[x]), attrs))
        tag_specs[tag] = None

        i = self.tag_condition_satisfaction.index(False)
        next_condition = self.tag_conditions[i]
        all_match = True
        for key, value in next_condition.items():
            if not (key in tag_specs and tag_specs[key] == value):
                all_match = False
                break

        self.tag_condition_satisfaction[i] = all_match

        if self.is_detected and self.data_key in attrs:
            self.data = attrs[self.data_key]

    def process_end_tag(self, tag):
        if self.data or not self.is_detected:
            return

        if tag == self.end_tag:
            self.data = self._data_buffer
        else:
            self.process_data(to_string(tag))

    def process_data(self, data):
        if not self.data and self.is_detected and not self.data_key:
            self._data_buffer += data

    @property
    def is_detected(self):
        unsatisfied_conditions = list(filter(lambda x: not x, self.tag_condition_satisfaction))
        return len(unsatisfied_conditions) == 0

    def postprocess(self):
        '''
        This method is meant to be overridden. It only gets triggered when self.data isn't None
        '''
        pass


class HTMLVariableCollection(list):
    def process_start_tag(self, tag, attrs):
        for x in self:
            x.process_start_tag(tag, attrs)

    def process_data(self, data):
        for x in self:
            x.process_data(data)

    def process_end_tag(self, tag):
        for x in self:
            x.process_end_tag(tag)

    def postprocess(self):
        for x in self:
            if x.data:
                x.postprocess()

    @property
    def data(self):
        for x in self:
            if x.data:
                return x.data
        return None


def determine_end_tag(tag_conditions):
    for key in tag_conditions[-1]:
        return key.split('.')[0]


def to_string(tag, attrs=None):
    to_return = '<' + ('/' if not attrs else '') + tag
    if attrs:
        for key, value in attrs.items():
            to_return += ' {}="{}"'.format(key, value)
    return to_return + '>'
