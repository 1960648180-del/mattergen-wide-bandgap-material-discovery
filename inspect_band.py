import gpaw, inspect
c = gpaw.GPAW(mode='pw')
for cls in type(c).__mro__:
    if 'band_structure' in cls.__dict__:
        fn = cls.__dict__['band_structure']
        print('owner:', cls)
        print('sig:', inspect.signature(fn))
        print('doc:', (fn.__doc__ or '')[:1200])
        break
print('=== set ===')
print('set sig:', inspect.signature(c.set))
print('set doc:', (c.set.__doc__ or '')[:300])
