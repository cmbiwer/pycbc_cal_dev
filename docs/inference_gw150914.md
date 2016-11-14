###############################################################################
PyCBC inference GW150914 example
###############################################################################

===================
Introduction
===================

This page gives details on how to do a simple parameter estimation analysis of
GW150914 using ``pycbc_inference``. This example is meant to finish in a
short amount of time (~6 hours on ``sugwg-condor``).

You can check your results against: https://arxiv.org/abs/1602.03840

For example, the paper measured that chirp mass is ~31 solar masses, q is ~1.3,
and the effective spin parameter is ~-0.07.

Note that there are a few difference between this example and the analysis in
the paper. For example, here we use a low-frequency cutoff of 30Hz instead
of 20Hz, and using only 4 seconds of data instead of 8 seconds. Also LALInference
has more features, eg. a bucket of different jump proposals, PSD fitting, and
calibration marginalization to keep in mind when comparing.

To increase the number of independent samples use more walkers and iterations.
Remember if you're not using a burn-in option with ``pycbc_inference``, you'll
want to discard some of the samples at the start (about a couple autocorrelation
lengths).

Within a couple hundred samples you'll see structure in the posteriors, and they'll
slowly "move" as the sampler continues.

===================
Instructions
===================

Copy the ``inference.ini`` section below into a file named ``inference.ini``.

Copy the ``run_pycbc_inference.sh`` section below into a file named ``run_pycbc_inference.sh``.

Run:

```
sh run_pycbc_inference.sh
```

See the appendix on this page for a simple condor example.

See the appendix on how to plot posterior.

===================
``inference.ini``
===================

```

; example configuration file for pycbc_inference GW150914 example
; values here are hardcoded for a simple example
; note options can be changed using --config-overrides with pycbc_inference

[variable_args]
; waveform parameters that will vary in MCMC
; not shown parameters are spin1x, spin1y, spin2x, spin2y
; alternatively options for spin magnitude and angles exist
tc =
mchirp =
q =
spin1z =
spin2z =
distance =
coa_phase =
inclination =
polarization =
ra =
dec =

[static_args]
; waveform parameters that will not change in MCMC
approximant = SEOBNRv2_ROM_DoubleSpin
f_lower = 28.0

[prior-tc]
; prior for coalescence time
name = uniform
min-tc = 1126259462.2
max-tc= 1126259462.6

[prior-mchirp]
; prior for chirp mass
name = uniform
min-mchirp = 7.
max-mchirp = 70.

[prior-q]
; prior for mass ratio (m1 > m2)
name = uniform
min-q = 1.
max-q = 5.

[prior-spin1z]
; prior for component spin of m1
name = uniform
min-spin1z = -0.9
max-spin1z = 0.9

[prior-spin2z]
; prior for component spin of m2
name = uniform
min-spin2z = -0.9
max-spin2z = 0.9

[prior-distance]
; prior for distance
name = uniform
min-distance = 10
max-distance = 500

[prior-coa_phase]
; prior for coalescence phase
name = uniform_angle

[prior-inclination]
; prior for inclination angle
name = uniform_angle
min-inclination = 0
max-inclination = 1

[prior-ra+dec]
; prior for right acension and declination
name = uniform_sky

[prior-polarization]
; prior for polarization angle
name = uniform_angle

```

===================
``run_pycbc_inference.sh``
===================

```
#! /bin/bash
# example of how to run pycbc_inference on GW150914

# time of event
TRIGGER_TIME=1126259462.0
TRIGGER_TIME_INT=${TRIGGER_TIME%.*}

# output file option
OUTPUT=gw150914_example_emcee_pt.hdf

# inference configuration file that holds prior information
CONFIG_PATH=inference.ini

# amount of data to read for analysis (2*${SEGLEN} is amount of data read)
SEGLEN=2
GPS_START_TIME=$((${TRIGGER_TIME_INT} - ${SEGLEN}))
GPS_END_TIME=$((${TRIGGER_TIME_INT} + ${SEGLEN}))

# amount of data to read for PSD estimation
PSD_START_TIME=$((${TRIGGER_TIME_INT} - 300))
PSD_END_TIME=$((${TRIGGER_TIME_INT} + 2048 - 300))

# IFOs to use in analysis
IFOS="H1 L1"

# sample rate to use for data and waveform generation
SAMPLE_RATE=16384

# minimum frequency to begin calculating posteriors
F_MIN=30.

# number of chains in MCMC samplers
N_WALKERS=5000

# number of iterations to progress each chain
N_ITERATIONS=5000

# prints out progress of MCMC every ${N_CHECKPOINT} iteration
N_CHECKPOINT=100

# what kind of backend to use for filtering
PROCESSING_SCHEME=cpu
NPROCS=12

# number of temperatures to use in parallel tempered sampler
NTEMPS=5

# run sampler
echo "Running MCMC"
echo "============================"
pycbc_inference --verbose \
    --instruments ${IFOS} \
    --frame-type H1:H1_HOFT_C02 L1:L1_HOFT_C02 \
    --channel-name H1:H1:DCS-CALIB_STRAIN_C02 L1:L1:DCS-CALIB_STRAIN_C02 \
    --gps-start-time ${GPS_START_TIME} \
    --gps-end-time ${GPS_END_TIME} \
    --psd-estimation median \
    --psd-start-time ${PSD_START_TIME} \
    --psd-end-time ${PSD_END_TIME} \
    --psd-segment-stride 8 \
    --psd-segment-length 16 \
    --sample-rate ${SAMPLE_RATE} \
    --pad-data 8 \
    --low-frequency-cutoff ${F_MIN} \
    --strain-high-pass 30 \
    --processing-scheme ${PROCESSING_SCHEME} \
    --sampler emcee_pt \
    --skip-burn-in \
    --likelihood-evaluator gaussian \
    --checkpoint-interval ${N_CHECKPOINT} \
    --checkpoint-fast \
    --ntemps ${NTEMPS} \
    --nwalkers ${N_WALKERS} \
    --niterations ${N_ITERATIONS} \
    --config-file ${CONFIG_PATH} \
    --output-file ${OUTPUT} \
    --nprocesses ${NPROCS}
```

===================
Appendix: Sampler
===================

Here we use the parallel tempered sampler implemented in emcee
(http://dan.iel.fm/emcee/current/user/pt/).

This is denoted by ``--sampler emcee_pt --skip-burn-in --ntemps 5`` with
``pycbc_inference``. The skip burn-in means there is no annealing period.
Here we set the number of temperatures to 5.

There are two other samplers that can be used. 

There is another sampler implemented in emcee without temperatures. You can
give ``--sample emcee --skip-burn-in`` and remove ``--ntemps 5`` to use it.

In order to use kombine (https://github.com/bfarr/kombine) remove the
``--ntemps`` option and change to ``--samplers kombine``. You can remove
``--skip-burn-in`` with kombine if you want to use kombine's internal test.

In general I've found the ``emcee_pt`` sampler to be more precision though less
accurate than the other two. That's something I'm looking at now.

===================
Appendix: Condor
===================

You can make a condor submit file and run that instead since these can take
awhile. An example of a simple condor submit script:
```
universe = vanilla
executable = run_pycbc_inference.sh
arguments =

get_env = True

output = inference_emcee_pt_gw150914_$(Cluster).out
error = inference_emcee_pt_gw150914_$(Cluster).err
log = inference_emcee_pt_gw150914_$(Cluster).log

accounting_group = sugwg.astro

request_memory = 50G
request_disk = 3.5G

queue
```

Remember to:
```
chmod +x run_pycbc_inference.sh
```


===================
Appendix: Plot posterior
===================

There is an executable already written to plot the posterior named
``pycbc_inference_plot_posterior``.

Example of how to use it is:

```
#! /bin/bash

HTML_DIR=${HOME}/public_html/inference_example/gw150914
mkdir -p ${HTML_DIR}

INPUT_FILE=gw150914_example_emcee_pt.hdf

pycbc_inference_plot_posterior --input-file ${INPUT_FILE} \
    --output-file ${HTML_DIR}/posterior.png \
    --hide-contours --hide-density \
    --quantiles 0.05 .5 0.95 \
    --iteration 2399
```

Here we plot the 90% credible interval (the quantiles option), and choose to
plot only the 2399th iteration.

You can use the ``--thin-start``, ``--thin-interval``, and ``--thin-end`` options
to pick out every i-th sample between a start and an end.

Other plotting executables for samples, autocorrelation length, etc. all start with
``pycbc_inference_plot_*`` if you have pycbc installed.
