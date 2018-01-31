#
# This file is part of PyFOPPL, an implementation of a First Order Probabilistic Programming Language in Python.
#
# License: MIT (see LICENSE.txt)
#
# 17. Jan 2018, Tobias Kohn
# 31. Jan 2018, Tobias Kohn
#
from .code_objects import *
from .code_types import *
from enum import *

#########################################################################

class DistributionType(Enum):

    CONTINUOUS = "continuous"
    DISCRETE   = "discrete"


#########################################################################

class Distribution(object):

    def __init__(self, name:str, distributions_type:DistributionType=None, params:list=None,
                 *, has_transform_flag:bool=False, vector_sample:bool=False,
                 transform_forward:str=None, transform_inverse:str=None,
                 transform_distribution:str=None, transforms:tuple=None,
                 foppl_name:str=None, python_name:str=None):
        assert type(name) is str
        self.name = name
        self.foppl_name = name.lower() if foppl_name is None else foppl_name
        self.python_name = name if python_name is None else python_name
        if distributions_type is None:
            self.distribution_type = DistributionType.CONTINUOUS
        else:
            self.distribution_type = distributions_type
        if params is None:
            self.params = []
        else:
            self.params = params
        self.has_transform_flag = has_transform_flag
        self._vector_sample = vector_sample
        if transforms is not None:
            fd, inv, dist = transforms
            transform_forward = fd if transform_forward is None else transform_forward
            transform_inverse = inv if transform_inverse is None else transform_inverse
            transform_distribution = dist if transform_distribution is None else transform_distribution
        self.transform_forward = transform_forward
        self.transform_inverse = transform_inverse
        self.transform_distribution = transform_distribution

    def check_arguments(self, args:list, throw_error:bool=False):
        return True

    def create_code(self, args:list):
        return "dist.{}({})".format(self.python_name, ', '.join(args))

    def get_parameter_count(self):
        return len(self.params)

    def get_sample_size(self, args:list):
        return 1

    def get_sample_type(self, args:list):
        if self.distribution_type == DistributionType.CONTINUOUS:
            result = FloatType()
        else:
            result = IntegerType()

        if self._vector_sample and len(args) > 0:
            if isinstance(args[0], SequenceType):
                result = ListType(result, args[0].size)

        return result

    def _get_support_size(self, arg):
        if isinstance(arg, CodeValue) and type(arg.value) is list:
            if all([type(item) is list for item in arg.value]):
                return max([len(item) for item in arg.value])
            else:
                return len(arg.value)

        elif isinstance(arg, CodeVector) and len(arg.items) > 0:
            _is_vector = lambda v: isinstance(v, CodeVector) or (isinstance(v, CodeValue) and type(v.value) is list)
            if all([_is_vector(item) for item in arg.items]):
                return max([len(item) for item in arg.items])
            else:
                return len(arg.items)

        elif isinstance(arg, CodeDataSymbol) and len(arg) > 0:
            if all([type(item) is list for item in arg.node.data]):
                return max([len(item) for item in arg.node.data])
            else:
                return len(arg.node.data)

        elif isinstance(arg.code_type, SequenceType):
            if isinstance(arg.code_type.item_type, SequenceType):
                return arg.code_type.item_type.size
            else:
                return arg.code_type.size

        else:
            return None

    def get_support_size(self, args:list):
        return self._get_support_size(args[0])

    def get_transformations(self):
        return self.transform_forward, self.transform_inverse, self.transform_distribution

    @property
    def is_continuous(self):
        return self.distribution_type == DistributionType.CONTINUOUS

    @property
    def is_discrete(self):
        return self.distribution_type == DistributionType.DISCRETE

    @property
    def parameter_count(self):
        return self.get_parameter_count()

    @property
    def transformations(self):
        return self.get_transformations()



#########################################################################

class BinomialDistribution(Distribution):

    def get_sample_type(self, args:list):
        if self._vector_sample and len(args) >= 2:
            if isinstance(args[1], SequenceType):
                result = ListType(IntegerType(), args[1].size)

        return IntegerType()

    def get_support_size(self, args:list):
        return self._get_support_size(args[1])


class CategoricalDistribution(Distribution):

    def get_sample_type(self, args:list):
        if len(args) == 1:
            arg = args[0]
            if isinstance(arg, ListType) and isinstance(arg.item_type, ListType):
                return ListType(IntegerType, arg.size)
            if isinstance(arg, SequenceType):
                return IntegerType()

        return AnyType()



#########################################################################

distributions = {
    Distribution('Bernoulli',   DistributionType.DISCRETE,   ['probs']),
    Distribution('Beta',        DistributionType.CONTINUOUS, ['concentration0', 'concentration1']),
    BinomialDistribution(
                 'Binomial',    DistributionType.CONTINUOUS, ['total_count', 'probs']),
    CategoricalDistribution(
                 'Categorical', DistributionType.DISCRETE,   ['probs']),
    Distribution('Cauchy',      DistributionType.CONTINUOUS, ['loc', 'gamma']),
    Distribution('Dirichlet',   DistributionType.CONTINUOUS, ['concentration0'],
                 vector_sample=True),
    Distribution('Discrete',    DistributionType.DISCRETE,   None),
    Distribution('Exponential', DistributionType.CONTINUOUS, ['rate'],
                 has_transform_flag=True),
    Distribution('Gamma',       DistributionType.CONTINUOUS, ['concentration0', 'concentration1'],
                 has_transform_flag=True, transforms=('bijector.Log', 'bijector.Exp', 'LogGamma')),
    Distribution('HalfCauchy',  DistributionType.CONTINUOUS, ['loc', 'gamma'], foppl_name='half_cauchy'),
    Distribution('LogGamma',    DistributionType.CONTINUOUS, ['concentration0', 'concentration1'],
                 has_transform_flag=True, foppl_name=''),
    Distribution('LogNormal',   DistributionType.CONTINUOUS, ['loc', 'scale'], foppl_name='log_normal'),
    Distribution('Multinomial', DistributionType.DISCRETE,   ['total_count', 'probs']),
    Distribution('MultivariateNormal',
                                DistributionType.CONTINUOUS, ['loc', 'covariance_matrix'], foppl_name='mvn',
                                vector_sample=True),
    Distribution('Normal',      DistributionType.CONTINUOUS, ['loc', 'scale']),
    Distribution('Poisson',     DistributionType.DISCRETE,   ['rate']),
    Distribution('Uniform',     DistributionType.CONTINUOUS, ['low', 'high'])
}

distributions_map = { d.foppl_name: d.python_name for d in distributions if d.name != '' }

foppl_distributions_map = { d.foppl_name: d for d in distributions if d.foppl_name != '' }

def get_distribution_for_name(name: str):
    for dist in distributions:
        if dist.name == name or dist.python_name == name or dist.foppl_name == name:
            return dist
    return None


def get_result_type(name: str, args: list):
    dist = get_distribution_for_name(name)
    if dist is not None:
        return dist.get_sample_type(args)
    return AnyType()
