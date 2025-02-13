# Content Moderation System

A scalable content moderation system built using FastAPI, Celery, Redis, PostgreSQL, and Docker. This project integrates with OpenAI’s moderation API to process text content, implements rate limiting and caching, and leverages asynchronous task processing for high throughput.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [System Architecture](#system-architecture)
- [Setup Instructions](#setup-instructions)
- [API Documentation](#api-documentation)
- [Database Migrations & Indexing](#database-migrations--indexing)
- [Testing](#testing)
- [Performance Considerations](#performance-considerations)
- [Load Testing](#load-testing)
- [Docker & Docker Compose](#docker--docker-compose)
- [License](#license)

## Overview

This project implements a robust content moderation system to screen text content using AI. Key components include:

- **Content Processing Service** using FastAPI.
- **Asynchronous Task Processing** with Celery.
- **Caching** using Redis to reduce redundant calls.
- **Rate Limiting** (5 requests per minute per IP using Slowapi).
- **Database Storage** using PostgreSQL with efficient indexing.
- **Monitoring** through Prometheus metrics.

## Features

- **API for Text Moderation:**  
  - Accept text content for moderation.
  - Integrate with OpenAI’s moderation API.
  - Fallback responses if the AI service is unavailable.
- **Asynchronous Processing:**  
  - Background tasks with Celery (with retry and exponential backoff).
  - Support for polling task status via dedicated endpoints.
- **Caching & Rate Limiting:**  
  - Redis caching of moderation results for 10 minutes.
  - Slowapi-based rate limiting (5 requests per minute per IP).
- **Database Management:**  
  - Moderation results stored in PostgreSQL.
  - Database migrations managed with Alembic.
  - Indexes added on key columns (e.g., model, created_at).
- **Monitoring & Logging:**  
  - Prometheus metrics exposed for monitoring.
  - Structured logging and health-check endpoints.

## System Architecture

- **Microservices Architecture:**  
  All components are containerized using Docker. Separate containers are used for the FastAPI app, Celery worker, Redis, and PostgreSQL.
- **Asynchronous Communication:**  
  Celery tasks decouple intensive AI queries from synchronous API responses.
- **Caching & Rate Limiting:**  
  Redis is used both for caching AI responses and for storing rate limiting counters.
- **Database Indexing:**  
  Alembic manages database migrations, and indexes (e.g., on `model` and `created_at`) enable rapid querying.

## Setup Instructions

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/your-repo.git
   cd your-repo
