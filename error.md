---------------------------------------------------------------------------
ValueError                                Traceback (most recent call last)
Cell In[311], line 60
     56     sliders=[slider],
     57     updatemenus=[play],
     58 )
     59 
---> 60 fig.show()

File c:\Dev\controlbox_db_ins_raw_plots\.venv\Lib\site-packages\plotly\basedatatypes.py:3420, in BaseFigure.show(self, *args, **kwargs)
   3387 """
   3388 Show a figure using either the default renderer(s) or the renderer(s)
   3389 specified by the renderer argument
   (...)   3416 None
   3417 """
   3418 import plotly.io as pio
-> 3420 return pio.show(self, *args, **kwargs)

File c:\Dev\controlbox_db_ins_raw_plots\.venv\Lib\site-packages\plotly\io\_renderers.py:415, in show(fig, renderer, validate, **kwargs)
    410     raise ValueError(
    411         "Mime type rendering requires ipython but it is not installed"
    412     )
    414 if not nbformat or Version(nbformat.__version__) < Version("4.2.0"):
--> 415     raise ValueError(
    416         "Mime type rendering requires nbformat>=4.2.0 but it is not installed"
    417     )
    419 display_jupyter_version_warnings()
    421 ipython_display.display(bundle, raw=True)

ValueError: Mime type rendering requires nbformat>=4.2.0 but it is not installed