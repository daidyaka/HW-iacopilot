package com.example.booking.domain;

import java.time.Instant;
import java.util.UUID;

public class Reservation {
    private final String id;
    private final String roomId;
    private final String userId;
    private final Instant createdAt;
    private ReservationStatus status;

    public Reservation(String roomId, String userId) {
        this.id = UUID.randomUUID().toString();
        this.roomId = roomId;
        this.userId = userId;
        this.createdAt = Instant.now();
        this.status = ReservationStatus.NEW;
    }

    public String getId() { return id; }
    public String getRoomId() { return roomId; }
    public String getUserId() { return userId; }
    public Instant getCreatedAt() { return createdAt; }
    public ReservationStatus getStatus() { return status; }

    public void markPendingPayment() { if (status == ReservationStatus.NEW) status = ReservationStatus.PENDING_PAYMENT; }
    public void confirm() { if (status == ReservationStatus.PENDING_PAYMENT) status = ReservationStatus.CONFIRMED; }
    public void cancel() { if (status != ReservationStatus.COMPLETED && status != ReservationStatus.CANCELLED) status = ReservationStatus.CANCELLED; }
    public void expire() { if (status == ReservationStatus.NEW || status == ReservationStatus.PENDING_PAYMENT) status = ReservationStatus.EXPIRED; }
}
