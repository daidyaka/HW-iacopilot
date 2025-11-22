package com.example.payment.api;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@RequestMapping("/api/payments")
public class PaymentController {

    @PostMapping("/simulate")
    public ResponseEntity<Map<String, Object>> simulate() {
        return ResponseEntity.ok(Map.of("paymentStatus", "APPROVED"));
    }
}
