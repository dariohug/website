---
title: "Bachelor Thesis: CAN-to-RF Telemetry"
---

My bachelor thesis, *CAN-to-RF Telemetry System for Solar Racing Vehicles*,
grew out of my work with [aCentauri Solar Racing](/solar-racing/). During a
race the strategy car follows the solar car. It needs a live view of what is
happening on the vehicle bus. Race routes are remote, so the link has to be
autonomous, low-power and secure without any cellular coverage.

The system is a dual-link telemetry unit built around an STM32L4A6
microcontroller. A long-range LoRa downlink at 868/915 MHz is paired with a
2.4 GHz FLRC uplink carrying about 30 kbit/s of CAN payload. Every packet is
encrypted and authenticated with AES-128 in counter mode plus CMAC. The chip's
crypto accelerator handles this in roughly 30 µs, so strong cryptography still
fits within real-time performance on a low-power MCU. A link-budget model
predicted about 2.8 km of range on the MHz link and 550 m on the GHz link.
Field tests confirmed a real operating range of 520 m. The result is a secured,
medium-range CAN telemetry link built within the power, size and regulatory
limits of a solar race car, using commodity hardware.

The full thesis is below, and the PDF also lives in my
[notes folder](/documents/university/bachelors_thesis/).

<div class="pdf-embed"><embed src="/documents/university/bachelors_thesis/bsc_thesis_dario_hug.pdf" type="application/pdf"></div>

[Download the PDF](/documents/university/bachelors_thesis/bsc_thesis_dario_hug.pdf)
