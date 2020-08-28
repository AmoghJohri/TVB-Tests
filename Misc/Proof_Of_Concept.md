# Proof Of Concept

The followiing serves as the proof of concept for the work-flow adoped in *main_temporalDomain.c*. This is meant for an easier understanding, reviewing and debugging of the code.

## Inputs:
1. **HRF_length**: Length of the Hemodynamic Response Function (seconds)
2. **HRF_samples**: Length of the time-series of the Hemodynamic Response Function (provided as input in param_set.txt)
3. **BOLD_TR**: Repetition Time for the BOLD simulations (milliseconds, provided as input in param_set.txt)
4. **total_duration**: Total duration for the simulation (milliseconds, provided as input in param_set.txt)
5. **model_dt**: Sampling period of the monitor (milliseconds). Example:
    > `model_dt = 1` corresponds to 1000 samples per second.
6. **dt**: Integration time-step for the monitor (milliseconds)
    > `model_dt/dt` steps (rounded to the nearest integer) are averaged for every sample

## Proof:
BOLD response is obtained by convolving the simulated nerual response and the Hemodynamic Response Function (HRF). This can be considered as the sum of shifted-scaled HRF signals, where the scaling factor is equal to the neural response at the 0<sup>th</sup> time-step of individual HRF signals.

![BOLD Response Convolution](Images/Figure_1.png)

The above figure shows shifted signals (first three panes) and their sum (fourth pane). Indeed, this is what we aim to do while obtaining the BOLD response, where the individual HRF signals are also scaled by the corresponding neural response.

Suppose the neural response function as **X** and the HRF as **H**. Then,
> `X:`    `x`<sub>`1`</sub>`,` `x`<sub>`2`</sub>`,` `x`<sub>`3`</sub>`, .....,` `x`<sub>`n`</sub>
<br> `H:` `h`<sub>`1`</sub>`,` `h`<sub>`2`</sub>`,` `h`<sub>`3`</sub>`, .....,` `h`<sub>`m`</sub>


Where the length of neural response is *n*, and the length of HRF is *m*.

**Note:** 
* The HRF signal has been upsampled from `HRF_samples to (HRF_length x 1000)/model_dt`
* We obtain the length of signals by - \<duration of signal in second>/model_dt.
<br> Hence, `n = total_duration/model_dt` and `m = length of upsampled HRF`. The factor of 1000 is introduces as the we deal in seconds with for HRF as opposed to milliseconds (like everything else). 

The BOLD simulation is obtained by a linear-convolution of the two-signals. Usually, this is a computationally demanding procedure, however, we can use a property of BOLD response to perform it differently.

The BOLD simulation output only contains those time-steps which coincide with BOLD_TR. These time-steps can be determined as:
> `time_steps % BOLD_TR_steps == 0` <br>
  `where, BOLD_TR_steps = BOLD_TR/model_dt` <br>
  `and, time_steps = total_duration/model_dt`

Let us suppose one such time-step to be **k**. Now for every k we have:
* The time-steps which determine the BOLD response at k<sup>th</sup> step lie in the range of `[k-m, k]`, i.e. the BOLD response on k<sup>th</sup> time-step is the sum of scaled-shifted HRF signals, where the number of such signals are m (from the one which starts at (k-m)<sup>th</sup> time-step to the one which starts at k<sup>th</sup> time-step), where each of these are scaled by the corresponding neural response.
* > Hence, BOLD response at k,<sup>th</sup> step = 
 `x`<sub>`k`</sub>`h`<sub>`1`</sub> `+ x`<sub>`k-1`</sub>`h`<sub>`2`</sub> `,......+ x`<sub>`k-m`</sub>`h`<sub>`m`</sub> 
* To obtain this, we take a dot-product of the simulated neural response with the flipped-upsampled hemodynamic response function (as shown above).
* The simulated neural response is stored in a circular-buffer (hence, the buffer is not in a temporally sequential order). The maintain the corresponding order between the HRF array, we roll the array over by `current_time_steps % m`, and then proceed with the dot product. This maintains the mutual ordering between the arrays. 

``` C
/* taking the dot product (to mimic convolution) between the neural states and the HRF (which has been reversed beforehand, and is shited by 'init' to align it to the neural response) */
/* this is performed at every time-step falling at the BOLD Repetition Time */
float shifted_reversed_dot_product(float* sigA, float* sigB, int n, int init)
{
    float output = 0.;
    for(int i = 0; i < n; i++)
    {
        output = output + sigA[i]*sigB[(i + init)%n];
    }
    return output;
}
```