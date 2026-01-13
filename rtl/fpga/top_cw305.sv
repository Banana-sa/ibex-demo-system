// Copyright lowRISC contributors.
// Licensed under the Apache License, Version 2.0, see LICENSE for details.
// SPDX-License-Identifier: Apache-2.0

// This is the top level SystemVerilog file that connects the IO on the board to the Ibex Demo System.
module top_cw305 (
  // These inputs are defined in data/pins_cw305.xdc
  input  logic          I_pll_clk1,
  input  logic          I_cw_clkin,
  input  logic          IO_RST_N,
  input  logic          IO3,
  input  logic          J16,
  input  logic          K16,
  input  logic          L14,
  input  logic          K15,
  output logic          IO4,
  output logic [ 2:0]   LED,
  input  logic          UART_RX,
  output logic          UART_TX
);
  parameter SRAMInitFile = "";

  logic clk_sys, rst_sys_n;
  reg [24:0] clock_heartbeat;

  assign LED[0] = clock_heartbeat[24];
  assign LED[1] = ~UART_RX || ~UART_TX;
  assign LED[2] = IO4;

  always @(posedge clk_sys) clock_heartbeat <= clock_heartbeat +  25'd1;

  // Instantiating the Ibex Demo System.
  ibex_demo_system #(
      .PwmWidth(1),
    .SRAMInitFile(SRAMInitFile)
  ) u_ibex_demo_system (
    //input
    .clk_sys_i(clk_sys),
    .rst_sys_ni(rst_sys_n),

      .uart_rx_i(UART_RX),

    //output
      .pwm_o(),
    .uart_tx_o(UART_TX),

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

    .trst_ni(1'b1),
    .tms_i(1'b0),
    .tck_i(1'b0),
    .td_i(1'b0),
    .td_o()
  );

  // clock source select:
  logic chosen_clock;
  BUFGMUX_CTRL U_clock_source_select (
     .O         (chosen_clock),
     .I0        (I_pll_clk1),
     .I1        (I_cw_clkin),
     .S         (J16) // J16 selects the clock; 0=on-board PLL, 1=from CW HS2 pin
  );


  // Generating the system clock and reset for the FPGA.
  clkgen_xil7series clkgen(
    .IO_CLK     (chosen_clock),
    .IO_RST_N,
    .clk_sys,
    .rst_sys_n
  );

endmodule
