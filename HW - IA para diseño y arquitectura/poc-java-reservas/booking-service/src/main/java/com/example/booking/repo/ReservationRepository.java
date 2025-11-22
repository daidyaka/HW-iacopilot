package com.example.booking.repo;

import com.example.booking.domain.Reservation;

import java.util.Collection;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;

public class ReservationRepository {
    private final Map<String, Reservation> store = new ConcurrentHashMap<>();

    public Reservation save(Reservation r) {
        store.put(r.getId(), r);
        return r;
    }

    public Optional<Reservation> findById(String id) { return Optional.ofNullable(store.get(id)); }

    public Collection<Reservation> findAll() { return store.values(); }
}
