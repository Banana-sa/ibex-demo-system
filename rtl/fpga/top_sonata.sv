// Copyright lowRISC contributors.
// Licensed under the Apache License, Version 2.0, see LICENSE for details.
// SPDX-License-Identifier: Apache-2.0

// Ibex demo system top level for the Sonata board
module top_sonata (
  input              main_clk,
  input              nrst_btn,

  output logic       led_bootok,
  output logic       led_halted,
  output logic       led_cheri,
  output logic       led_legacy,
  output logic [8:0] led_cherierr,

  output logic ser0_tx,
  input  logic ser0_rx,

  input  logic tck_i,
  input  logic tms_i,
  input  logic td_i,
  output logic td_o
);
  parameter SRAMInitFile = "";

  logic mainclk_buf;
  logic clk_sys;
  logic rst_sys_n;
  logic [7:0] reset_counter;

  logic pll_locked;
  logic rst_btn;


  assign led_bootok = rst_sys_n;

  ibex_demo_system #(
    .PwmWidth(12),
    .SRAMInitFile(SRAMInitFile)
  ) u_ibex_demo_system (
    .clk_sys_i(clk_sys),
    .rst_sys_ni(rst_sys_n),

    .uart_rx_i(ser0_rx),
    .uart_tx_o(ser0_tx),

    .pwm_o({led_cherierr, led_legacy, led_cheri, led_halted}),

    // Core2AXI 0 - Tie off (users can connect their own AXI slave)
    .core2axi0_aw_id_o    (),
    .core2axi0_aw_addr_o  (),
    .core2axi0_aw_len_o   (),
    .core2axi0_aw_size_o  (),
    .core2axi0_aw_burst_o (),
    .core2axi0_aw_lock_o  (),
    .core2axi0_aw_cache_o (),
    .core2axi0_aw_prot_o  (),
    .core2axi0_aw_region_o(),
    .core2axi0_aw_user_o  (),
    .core2axi0_aw_qos_o   (),
    .core2axi0_aw_valid_o (),
    .core2axi0_aw_ready_i (1'b0),
    .core2axi0_w_data_o   (),
    .core2axi0_w_strb_o   (),
    .core2axi0_w_last_o   (),
    .core2axi0_w_user_o   (),
    .core2axi0_w_valid_o  (),
    .core2axi0_w_ready_i  (1'b0),
    .core2axi0_b_id_i     ('0),
    .core2axi0_b_resp_i   ('0),
    .core2axi0_b_valid_i  (1'b0),
    .core2axi0_b_user_i   ('0),
    .core2axi0_b_ready_o  (),
    .core2axi0_ar_id_o    (),
    .core2axi0_ar_addr_o  (),
    .core2axi0_ar_len_o   (),
    .core2axi0_ar_size_o  (),
    .core2axi0_ar_burst_o (),
    .core2axi0_ar_lock_o  (),
    .core2axi0_ar_cache_o (),
    .core2axi0_ar_prot_o  (),
    .core2axi0_ar_region_o(),
    .core2axi0_ar_user_o  (),
    .core2axi0_ar_qos_o   (),
    .core2axi0_ar_valid_o (),
    .core2axi0_ar_ready_i (1'b0),
    .core2axi0_r_id_i     ('0),
    .core2axi0_r_data_i   ('0),
    .core2axi0_r_resp_i   ('0),
    .core2axi0_r_last_i   (1'b0),
    .core2axi0_r_user_i   ('0),
    .core2axi0_r_valid_i  (1'b0),
    .core2axi0_r_ready_o  (),

    // Core2AXI 1 - Tie off (users can connect their own AXI slave)
    .core2axi1_aw_id_o    (),
    .core2axi1_aw_addr_o  (),
    .core2axi1_aw_len_o   (),
    .core2axi1_aw_size_o  (),
    .core2axi1_aw_burst_o (),
    .core2axi1_aw_lock_o  (),
    .core2axi1_aw_cache_o (),
    .core2axi1_aw_prot_o  (),
    .core2axi1_aw_region_o(),
    .core2axi1_aw_user_o  (),
    .core2axi1_aw_qos_o   (),
    .core2axi1_aw_valid_o (),
    .core2axi1_aw_ready_i (1'b0),
    .core2axi1_w_data_o   (),
    .core2axi1_w_strb_o   (),
    .core2axi1_w_last_o   (),
    .core2axi1_w_user_o   (),
    .core2axi1_w_valid_o  (),
    .core2axi1_w_ready_i  (1'b0),
    .core2axi1_b_id_i     ('0),
    .core2axi1_b_resp_i   ('0),
    .core2axi1_b_valid_i  (1'b0),
    .core2axi1_b_user_i   ('0),
    .core2axi1_b_ready_o  (),
    .core2axi1_ar_id_o    (),
    .core2axi1_ar_addr_o  (),
    .core2axi1_ar_len_o   (),
    .core2axi1_ar_size_o  (),
    .core2axi1_ar_burst_o (),
    .core2axi1_ar_lock_o  (),
    .core2axi1_ar_cache_o (),
    .core2axi1_ar_prot_o  (),
    .core2axi1_ar_region_o(),
    .core2axi1_ar_user_o  (),
    .core2axi1_ar_qos_o   (),
    .core2axi1_ar_valid_o (),
    .core2axi1_ar_ready_i (1'b0),
    .core2axi1_r_id_i     ('0),
    .core2axi1_r_data_i   ('0),
    .core2axi1_r_resp_i   ('0),
    .core2axi1_r_last_i   (1'b0),
    .core2axi1_r_user_i   ('0),
    .core2axi1_r_valid_i  (1'b0),
    .core2axi1_r_ready_o  (),

    .trst_ni(rst_sys_n),
    .tms_i,
    .tck_i,
    .td_i,
    .td_o
  );

  // Produce 50 MHz system clock from 25 MHz Sonata board clock
  clkgen_sonata clkgen(
    .IO_CLK(main_clk),
    .IO_CLK_BUF(mainclk_buf),
    .clk_sys,
    .locked(pll_locked)
  );

  assign rst_btn = ~nrst_btn;

  rst_ctrl u_rst_ctrl (
    .clk_i       (mainclk_buf),
    .pll_locked_i(pll_locked),
    .rst_btn_i   (rst_btn),
    .rst_no      (rst_sys_n)
  );
endmodule
