// Copyright lowRISC contributors.
// Licensed under the Apache License, Version 2.0, see LICENSE for details.
// SPDX-License-Identifier: Apache-2.0

// This is the top level SystemVerilog file that connects the IO on the board to the Ibex Demo System.
module top_boolean (
  // These inputs are defined in data/pins_boolean.xdc
  input               IO_CLK,
  input               IO_RST,
  input  [15:0]       SW,
  input  [3:1]        BTN,
  output [15:0]       LED,
  output [5:0]        RGB_LED,
  input               UART_RX,
  output              UART_TX
);
  parameter SRAMInitFile = "";

  logic clk_sys, rst_sys_n;

  // Instantiating the Ibex Demo System.
  ibex_demo_system #(
      .PwmWidth(6),
    .SRAMInitFile(SRAMInitFile)
  ) u_ibex_demo_system (
    //input
    .clk_sys_i(clk_sys),
    .rst_sys_ni(rst_sys_n),

      .uart_rx_i(UART_RX),

    //output
      .pwm_o(RGB_LED),
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
    .tms_i(),
    .tck_i(),
    .td_i(),
    .td_o()
  );

  logic IO_RST_N;
  assign IO_RST_N = ~IO_RST;

  // Generating the system clock and reset for the FPGA.
  // Boolean has a 100 MHz clock.
  clkgen_xil7series clkgen(
    .IO_CLK,
    .IO_RST_N,
    .clk_sys,
    .rst_sys_n
  );

endmodule
