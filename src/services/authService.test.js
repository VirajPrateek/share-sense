import authService from './authService.js';
import pool from '../config/database.js';
import bcrypt from 'bcrypt';
import jwt from 'jsonwebtoken';

// Mock dependencies
jest.mock('../config/database.js');
jest.mock('bcrypt');
jest.mock('jsonwebtoken');

describe('AuthService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('register', () => {
    it('should successfully register a new user', async () => {
      const mockUser = {
        id: '123e4567-e89b-12d3-a456-426614174000',
        email: 'test@example.com',
        name: 'Test User',
        created_at: new Date(),
        updated_at: new Date()
      };

      // Mock database queries
      pool.query
        .mockResolvedValueOnce({ rows: [] }) // Check existing user
        .mockResolvedValueOnce({ rows: [mockUser] }); // Insert new user

      bcrypt.hash.mockResolvedValue('hashed_password');

      const result = await authService.register('test@example.com', 'password123', 'Test User');

      expect(result).toEqual(mockUser);
      expect(pool.query).toHaveBeenCalledTimes(2);
      expect(bcrypt.hash).toHaveBeenCalledWith('password123', 10);
    });

    it('should throw error if email already exists', async () => {
      pool.query.mockResolvedValueOnce({ rows: [{ id: 'existing-id' }] });

      await expect(
        authService.register('existing@example.com', 'password123', 'Test User')
      ).rejects.toThrow('Email already registered');
    });
  });

  describe('login', () => {
    it('should successfully login with valid credentials', async () => {
      const mockUser = {
        id: '123e4567-e89b-12d3-a456-426614174000',
        email: 'test@example.com',
        password_hash: 'hashed_password',
        name: 'Test User'
      };

      pool.query.mockResolvedValueOnce({ rows: [mockUser] });
      bcrypt.compare.mockResolvedValue(true);
      jwt.sign.mockReturnValue('mock_jwt_token');

      const result = await authService.login('test@example.com', 'password123');

      expect(result).toHaveProperty('user');
      expect(result).toHaveProperty('token');
      expect(result.user).not.toHaveProperty('password_hash');
      expect(result.token).toBe('mock_jwt_token');
    });

    it('should throw error for non-existent user', async () => {
      pool.query.mockResolvedValueOnce({ rows: [] });

      await expect(
        authService.login('nonexistent@example.com', 'password123')
      ).rejects.toThrow('Invalid credentials');
    });

    it('should throw error for invalid password', async () => {
      const mockUser = {
        id: '123e4567-e89b-12d3-a456-426614174000',
        email: 'test@example.com',
        password_hash: 'hashed_password',
        name: 'Test User'
      };

      pool.query.mockResolvedValueOnce({ rows: [mockUser] });
      bcrypt.compare.mockResolvedValue(false);

      await expect(
        authService.login('test@example.com', 'wrong_password')
      ).rejects.toThrow('Invalid credentials');
    });
  });

  describe('verifyToken', () => {
    it('should successfully verify valid token', async () => {
      const mockDecoded = {
        userId: '123e4567-e89b-12d3-a456-426614174000',
        email: 'test@example.com'
      };

      jwt.verify.mockReturnValue(mockDecoded);

      const result = await authService.verifyToken('valid_token');

      expect(result).toEqual(mockDecoded);
    });

    it('should throw error for invalid token', async () => {
      jwt.verify.mockImplementation(() => {
        throw new Error('Invalid token');
      });

      await expect(
        authService.verifyToken('invalid_token')
      ).rejects.toThrow('Invalid or expired token');
    });
  });

  describe('getUserById', () => {
    it('should return user for valid ID', async () => {
      const mockUser = {
        id: '123e4567-e89b-12d3-a456-426614174000',
        email: 'test@example.com',
        name: 'Test User',
        created_at: new Date(),
        updated_at: new Date()
      };

      pool.query.mockResolvedValueOnce({ rows: [mockUser] });

      const result = await authService.getUserById('123e4567-e89b-12d3-a456-426614174000');

      expect(result).toEqual(mockUser);
    });

    it('should throw error for non-existent user', async () => {
      pool.query.mockResolvedValueOnce({ rows: [] });

      await expect(
        authService.getUserById('non-existent-id')
      ).rejects.toThrow('User not found');
    });
  });
});
