import AnalysisConnector from './analysis';
import NavigationConnector from './navigation';
import RoutingConnector from './routing';
import StitchingConnector from './stitching';
import CloneConnector from './clone';

export const analysis = new AnalysisConnector();
export const navigation = new NavigationConnector();
export const routing = new RoutingConnector();
export const stitching = new StitchingConnector();
export const clone = new CloneConnector();