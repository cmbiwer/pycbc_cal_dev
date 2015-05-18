#! /bin/bash

DATABASE=../../test.db

ligolw_cbc_plotfm --ranking-stat "combined_far:Combined FAR (yr$^{-1}$)" --variables "injected_mchirp:Chirp Mass ($M_\odot$); injected_decisive_distance:Injected Decisive Distance (Mpc)" --logz  --sim-tag BNSALIGNED0INJ --livetime-program inspiral --logy  --colorbar  --recovery-table coinc_inspiral --user-tag fm_dist_v_param_BNSALIGNED0INJ_CAT_2_VETO --plot-y-function '3.48:$3.48$' --plot-y-function '5.23:$5.23$' --enable-output  --map-label nearby_insp --rank-by MIN --simulation-table sim_inspiral --tmp-space /usr1/${USER} ${DATABASE} --verbose
