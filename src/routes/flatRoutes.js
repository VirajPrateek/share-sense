import express from 'express';
import flatController from '../controllers/flatController.js';
import { authenticate } from '../middleware/auth.js';

const router = express.Router();

// All flat routes require authentication
router.use(authenticate);

// Flat management routes
router.post('/', flatController.createFlat.bind(flatController));
router.get('/', flatController.getUserFlats.bind(flatController));
router.get('/:flatId', flatController.getFlatById.bind(flatController));

// Flat member management routes
router.get('/:flatId/members', flatController.getFlatMembers.bind(flatController));
router.post('/:flatId/members', flatController.addMemberToFlat.bind(flatController));
router.delete('/:flatId/members/:userId', flatController.removeMemberFromFlat.bind(flatController));

export default router;
