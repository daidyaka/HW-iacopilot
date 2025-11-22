package com.example.booking.service;

import com.example.booking.domain.Reservation;
import com.example.booking.repo.ReservationRepository;
import org.springframework.stereotype.Service;

import java.util.Optional;

@Service
public class BookingService {
    private final ReservationRepository repository = new ReservationRepository();

    public Reservation create(String roomId, String userId) {
        Reservation r = new Reservation(roomId, userId);
        r.markPendingPayment(); // simulate immediate transition to pending payment
        r.confirm(); // simulate successful payment
        repository.save(r);
        return r;
    }

    public Optional<Reservation> get(String id) { return repository.findById(id); }
}
