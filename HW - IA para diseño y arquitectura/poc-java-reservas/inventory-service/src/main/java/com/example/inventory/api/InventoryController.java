package com.example.inventory.api;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/rooms")
public class InventoryController {

    @GetMapping
    public ResponseEntity<List<Map<String, Object>>> list() {
        return ResponseEntity.ok(List.of(
                Map.of("roomId", "room-1", "available", true),
                Map.of("roomId", "room-2", "available", true)
        ));
    }
}
