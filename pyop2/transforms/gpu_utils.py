from pyop2.global_kernel import AbstractGlobalKernel
    if isinstance(knl, AbstractGlobalKernel):
        from pyop2.op2 import compute_backend
        compute_backend.Parloop(knl, *args, **kwargs)()