package com.example.booking.api;

import com.example.booking.domain.Reservation;
import com.example.booking.service.BookingService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/bookings")
public class BookingController {

    private final BookingService bookingService;

    public BookingController(BookingService bookingService) {
        this.bookingService = bookingService;
    }

    @PostMapping
    public ResponseEntity<Reservation> create(@RequestBody Map<String, String> body) {
        String roomId = body.getOrDefault("roomId", "room-1");
        String userId = body.getOrDefault("userId", "user-1");
        return ResponseEntity.ok(bookingService.create(roomId, userId));
    }

    @GetMapping("/{id}")
    public ResponseEntity<?> get(@PathVariable String id) {
        return bookingService.get(id)
                .<ResponseEntity<?>>map(ResponseEntity::ok)
                .orElseGet(() -> ResponseEntity.notFound().build());
    }
}
